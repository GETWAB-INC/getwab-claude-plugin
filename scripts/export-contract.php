<?php
// Read declarations only: no Laravel bootstrap, database, remote API or env files.
require dirname(__DIR__, 3).'/vendor/autoload.php';
$controller = new App\Http\Controllers\GetwabPluginMcpController;
$method = new ReflectionMethod($controller, 'tools');
$registry = new ReflectionClass(App\Services\ProcurementPromptRegistry::class);
echo json_encode([
    'tools' => $method->invoke($controller),
    'playbooks' => $registry->getConstant('PLAYBOOKS'),
], JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
