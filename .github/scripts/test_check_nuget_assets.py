import copy
import tempfile
from pathlib import Path
import unittest

from check_nuget_assets import framework_id, validate


class AssetsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'fixture.csproj'
        self.project.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFrameworks>net45;netstandard2.0;net5.0</TargetFrameworks></PropertyGroup></Project>')
        self.assets = {
            'project': {'frameworks': {'net45': {}, 'netstandard2.0': {}, 'net5.0': {}}},
            'targets': {name: {'pkg/1.0': {'type': 'package'}} for name in (
                '.NETFramework,Version=v4.5', '.NETStandard,Version=v2.0', 'net5.0')},
        }

    def test_complete(self):
        validate(self.project, self.assets)
        self.assertEqual(framework_id('net461'), framework_id('.NETFramework,Version=v4.6.1'))
        self.assertEqual(framework_id('netcoreapp3.1'), framework_id('.NETCoreApp,Version=v3.1'))

    def test_missing_empty_and_project_only_targets(self):
        for case in ('missing', 'empty', 'project_only', 'rid_only'):
            with self.subTest(case=case):
                assets = copy.deepcopy(self.assets)
                key = '.NETFramework,Version=v4.5'
                if case == 'missing': del assets['targets'][key]
                elif case == 'empty': assets['targets'][key] = {}
                elif case == 'project_only': assets['targets'][key] = {'local/1.0': {'type': 'project'}}
                else: assets['targets'][key + '/win-x64'] = assets['targets'].pop(key)
                with self.assertRaisesRegex(ValueError, 'net45'):
                    validate(self.project, assets)

    def test_missing_declared_framework(self):
        del self.assets['project']['frameworks']['net45']
        with self.assertRaisesRegex(ValueError, 'Missing target framework'):
            validate(self.project, self.assets)

    def test_unsupported_name_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported target framework'):
            framework_id('net8.0-windows')


if __name__ == '__main__':
    unittest.main()
