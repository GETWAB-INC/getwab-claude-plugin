import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('adapter', ROOT / 'skills/research/scripts/adapter.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class CanonTests(unittest.TestCase):
    def test_every_tool_has_a_valid_acceptance_input(self):
        cases = json.loads((ROOT / 'tests/acceptance-cases.json').read_text())
        self.assertEqual(set(a.MAPPING['tools']), {case['tool'] for case in cases})
        for case in cases:
            a.translate_input(case['tool'], case['canonical_arguments'])

    def test_markdown_identity_preserved_and_canonical_label_extracted(self):
        row = {'uei':'[ABCDEF123456](https://www.getwab.com/app/entities/ABCDEF123456)', 'cage':'01234', 'name':'Example', 'unexpected':{'field':False}}
        before = copy.deepcopy(row)
        result = a.normalize_record('search_entities',row)
        self.assertEqual('ABCDEF123456',result['identifiers']['uei'])
        self.assertEqual(before,result['source_record'])
        self.assertEqual(before,row)
        self.assertEqual('source_role',result['organizations']['subject']['relationship_type'])

    def test_gsa_sin_is_not_naics(self):
        result = a.normalize_record('search_gsa_contracts',{'record_key':'1','category':'54151S','vendor':'Example'})
        self.assertEqual('54151S',result['classifications']['gsa_sin'][0]['code'])
        self.assertNotIn('naics',result['classifications'])

    def test_timezone_and_date_precision_are_preserved(self):
        record = a.normalize_record('search_opportunities',{'notice_id':'n','deadline_at':'2026-09-10T17:00:00-04:00'})
        self.assertEqual('2026-09-10T17:00:00-04:00',record['dates']['response_deadline_at'])
        record = a.normalize_record('search_subnet_opportunities',{'opportunity_id':'s','response_deadline':'2026-09-10'})
        self.assertEqual('2026-09-10',record['dates']['response_deadline_at'])

    def test_loading_time_is_not_source_updated_time(self):
        record = a.normalize_record('search_entities',{'uei':'ABCDEF123456','loaded_at':'2026-09-10'})
        self.assertNotIn('source_updated_at',record)
        self.assertEqual('2026-09-10',record['source_record']['loaded_at'])

    def test_vendor_directory_aliases_are_canonical(self):
        record = a.normalize_record('search_vendors',{'name':'Example','cage':'01234','uei':'ABCDEF123456'})
        self.assertEqual('Example',record['organizations']['vendor']['legal_name'])
        self.assertEqual('01234',record['organizations']['vendor']['cage'])

    def test_subaward_roles_and_negative_amount(self):
        r = a.normalize_record('search_subcontracts',{'record_key':'2','prime_name':'Prime','subcontractor_name':'Sub','amount':-25.5})
        self.assertEqual(-25.5,r['financials']['subaward_amount'])
        self.assertEqual('Sub',r['organizations']['subcontractor']['legal_name'])
        self.assertNotIn('vendor',r['organizations'])

    def test_invalid_and_unknown_values_are_not_fabricated(self):
        r = a.normalize_record('search_opportunities',{'deadline':'Sept 9 at noon','award_amount':'unknown'})
        self.assertIsNone(r['record_id'])
        self.assertNotIn('response_deadline_at',r['dates'])
        self.assertNotIn('award_amount',r['financials'])
        self.assertEqual('Sept 9 at noon',r['source_record']['deadline'])

    def test_forecast_sources_do_not_collide_and_dates_are_estimates(self):
        one = a.normalize_record('search_acquisition_forecasts',{'source':'fco','source_record_id':'1','estimated_award_at':'2027-01-02'})
        two = a.normalize_record('search_acquisition_forecasts',{'source':'apfs','source_record_id':'1'})
        self.assertNotEqual(one['record_id'],two['record_id'])
        self.assertEqual('2027-01-02',one['dates']['award_estimated_at'])
        self.assertNotIn('award_at',one['dates'])

    def test_auth_error_preserves_challenge_and_stops_records(self):
        p = {'result':{'isError':True,'_meta':{'mcp/www_authenticate':['Bearer test']},'content':[]}}
        r = a.normalize_result('search_awards',p)
        self.assertTrue(r['blocked'])
        self.assertEqual([],r['records'])
        self.assertEqual(p,r['source_result'])

    def test_unavailable_is_not_zero_coverage(self):
        r = a.normalize_result('search_entities',{'available':False,'total_matches':0,'records':[]})
        self.assertEqual('unavailable',r['coverage']['status'])

    def test_pagination_overrides_complete(self):
        r = a.normalize_result('search_entities',{'coverage_status':'complete','total_matches':400,'next_page':2,'records':[{'uei':'ABCDEF123456'}]})
        self.assertEqual('partial',r['coverage']['status'])

    def test_rankings_not_mislabeled_transactions_or_all_groups(self):
        r = a.normalize_result('analyze_awards',{'coverage_status':'complete','total_groups':1,'records':[{'uei':'ABCDEF123456','obligations':5}]})
        self.assertEqual('partial',r['coverage']['status'])
        self.assertIsNone(r['records'][0]['record_type'])
        self.assertEqual(5,r['records'][0]['source_record']['obligations'])

    def test_fallback_groups_remain_distinct(self):
        p = {'available':False,'records':[],'fallback_evidence':{'historical_contract_subawards':{'total_matches':1,'records':[{'record_key':'1','amount':5}]}}}
        r = a.normalize_result('search_subnet_opportunities',p)
        group = r['fallback_groups']['historical_contract_subawards']
        self.assertEqual('sam_contract_subawards',group['dataset_id'])
        self.assertEqual('partial',group['coverage']['status'])

    def test_array_to_scalar_rejects_loss(self):
        with self.assertRaises(ValueError):
            a.translate_input('search_subnet_opportunities',{'naics_codes':['541512','541519']})
        self.assertEqual({'naics':'541512'},a.translate_input('search_subnet_opportunities',{'naics_codes':['541512']}))

    def test_structured_award_codes(self):
        self.assertEqual({'naics':['541512'],'psc':['DA01']},a.translate_input('search_awards',{'naics_codes':['541512'],'psc_codes':['da01']}))

    def test_silently_ignored_upstream_dates_rejected(self):
        for tool in ('search_subcontracts','search_archived_opportunities'):
            with self.assertRaises(ValueError):
                a.translate_input(tool,{'query':'Example','date_from':'2026-01-01'})

    def test_unsupported_codes_enum_and_page_rejected(self):
        for tool, args in [('search_opportunities',{'query':'IT','naics_codes':['541512']}),('search_entities',{'query':'Example','page':False}),('search_subnet_opportunities',{'status':'invented'})]:
            with self.assertRaises(ValueError):
                a.translate_input(tool,args)

    def test_all_dataset_maps_preserve_unknown_fields(self):
        for dataset in a.MAPPING['datasets'].values():
            row = {dataset['record_keys'][0]:'ABCDEF123456','new_source_field':{'x':0}}
            r = a.normalize_record(dataset['tool'],row)
            self.assertEqual(row,r['source_record'])
            self.assertEqual(dataset['dataset_id'],r['dataset_id'])


if __name__ == '__main__':
    unittest.main()
