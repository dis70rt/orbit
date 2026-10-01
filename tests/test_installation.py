"""Installer behavior without invoking package managers or altering the desktop."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE / 'scripts'))
import install as installer
from installation.distributions import FAMILIES, detect
from installation.files import InstallPaths, deploy


class DistributionTests(unittest.TestCase):
    def test_native_ids_and_derivatives(self):
        cases = [('arch', '', 'arch'), ('fedora', '', 'fedora'),
                 ('ubuntu', 'debian', 'debian'), ('debian', '', 'debian'),
                 ('endeavouros', 'arch', 'arch'), ('linuxmint', 'ubuntu debian', 'debian')]
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory) / 'os-release'
            for identity, similar, family in cases:
                with self.subTest(identity=identity):
                    release.write_text(f'ID={identity}\nID_LIKE="{similar}"\n')
                    self.assertEqual(detect(release), FAMILIES[family])

    def test_unknown_distro_does_not_guess_package_manager(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory) / 'os-release'
            release.write_text('ID=nixos\n')
            with self.assertRaisesRegex(ValueError, '--skip-deps'):
                detect(release)

    def test_hyprland_only_added_when_missing_and_arch_never_partial_upgrades(self):
        for distribution in FAMILIES.values():
            self.assertNotIn('hyprland', distribution.install_command())
            self.assertIn('hyprland', distribution.install_command(hyprland_missing=True))
        arch = FAMILIES['arch'].install_command(yes=True)
        self.assertIn('--noconfirm', arch)
        self.assertNotIn('-Sy', arch)


class DeploymentTests(unittest.TestCase):
    def paths(self, directory):
        root = Path(directory)
        return InstallPaths(root / "data space's/orbit", root / 'bin/orbit', root / 'config/integration')

    def test_installed_launcher_runs_outside_checkout_and_upgrade_preserves_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.paths(directory)
            settings = paths.integration.parent / 'config.json'
            settings.parent.mkdir(parents=True)
            settings.write_text('{"custom": true}')
            deploy(SOURCE, paths, Path(sys.executable))
            result = subprocess.run([str(paths.executable), '--version'], cwd='/tmp',
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'Orbit v' + (SOURCE / 'VERSION').read_text().strip())
            self.assertTrue((paths.application / 'assets/icons/github.svg').is_file())
            self.assertFalse((paths.application / 'assets/banner.png').exists())
            self.assertNotIn('Projects/Orbit', (paths.integration / 'hyprland.conf').read_text())
            self.assertNotIn('Projects/Orbit', (paths.integration / 'hyprland.lua').read_text())
            deploy(SOURCE, paths, Path(sys.executable))
            self.assertEqual(settings.read_text(), '{"custom": true}')

    def test_existing_unrelated_files_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.paths(directory)
            paths.executable.parent.mkdir(parents=True)
            paths.executable.write_text('unrelated launcher')
            with self.assertRaisesRegex(ValueError, 'unrelated launcher'):
                deploy(SOURCE, paths, Path(sys.executable))
            self.assertEqual(paths.executable.read_text(), 'unrelated launcher')
            self.assertFalse(paths.application.exists())
            paths.executable.unlink()
            paths.application.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, 'unmanaged directory'):
                deploy(SOURCE, paths, Path(sys.executable))

    def test_failed_runtime_copy_preserves_installed_application(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.paths(directory)
            deploy(SOURCE, paths, Path(sys.executable))
            with patch('installation.files.shutil.copytree', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    deploy(SOURCE, paths, Path(sys.executable))
            self.assertTrue((paths.application / 'orbit/__main__.py').is_file())


class InstallerTests(unittest.TestCase):
    def test_root_invocation_is_rejected_before_package_commands(self):
        with patch('install.os.geteuid', return_value=0), patch('install.subprocess.run') as run, \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main([]), 1)
            run.assert_not_called()

    def test_dry_run_never_executes_commands_or_deploys(self):
        with patch('install.os.geteuid', return_value=1000), \
                patch('install.detect', return_value=FAMILIES['fedora']), \
                patch('install.subprocess.run') as run, patch('install.deploy') as copy, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(['--dry-run']), 0)
            run.assert_not_called()
            copy.assert_not_called()

    def test_missing_hyprland_prevents_deployment(self):
        with patch('install.os.geteuid', return_value=1000), \
                patch('install.shutil.which', return_value=None), patch('install.deploy') as copy, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(['--skip-deps']), 1)
            copy.assert_not_called()

    def test_invalid_runtime_prevents_deployment(self):
        with patch('install.os.geteuid', return_value=1000), \
                patch('install.shutil.which', return_value='/usr/bin/command'), \
                patch('install.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', 'missing gi')), \
                patch('install.deploy') as copy, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main(['--skip-deps']), 1)
            copy.assert_not_called()

    def test_package_failure_stops_installation(self):
        with patch('install.shutil.which', return_value='/usr/bin/command'), \
                patch('install.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['dnf'])):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, 'failed'):
                installer.install_dependencies(FAMILIES['fedora'], False)

    def test_success_checks_runtime_before_deploying(self):
        calls = []
        with patch('install.os.geteuid', return_value=1000), \
                patch('install.shutil.which', return_value='/usr/bin/command'), \
                patch('install.subprocess.run', side_effect=lambda *a, **k:
                      calls.append('probe') or subprocess.CompletedProcess([], 0, '', '')), \
                patch('install.deploy', side_effect=lambda *a: calls.append('deploy')), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.main(['--skip-deps']), 0)
        self.assertEqual(calls, ['probe', 'deploy'])


if __name__ == '__main__':
    unittest.main()
