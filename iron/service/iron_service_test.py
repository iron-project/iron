import os
import unittest
import records
import pysnooper

from iron.service.config_service import ConfigService
from iron.util.file_operator import FileUtil
from iron.service.chunk_service import ChunkServiceFactory
from iron.service.iron_service import IronService

class IronServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = ConfigService()

    def setUp(self):
        self.data_name = 'bin.tar.xz'
        self.testdata = 'testdata/bin.tar.xz'
        self.tmp_path = self.config.TMP_PATH
        self.tmp_data = os.path.join(self.tmp_path, self.data_name)
        self.iron = IronService()
        self.iron.mkdir('/', root_path=True)
        os.system('cp {} {}'.format(self.testdata, self.tmp_path))

    def tearDown(self):
        os.system('rm -rf {}'.format(self.tmp_path))

    # @pysnooper.snoop()
    def test_directory_operations(self):
        self.iron.mkdir('/foo')
        self.iron.mkdir('/foo')
        self.iron.lsdir('/')
        self.iron.lsdir('/bar')
        self.iron.mkdir('/bar')
        self.iron.lsdir('/')
        self.iron.lsdir('/bar')
        self.iron.mkdir('/bar/bla')
        self.iron.rmdir('/bar/')
        self.iron.rmdir('/bla')
        self.iron.rmdir('/foo')
        self.iron.lsdir('/')
        self.iron.lsdir('/foo')

    # @unittest.SkipTest
    def test_file_operations(self):
        remote_path = '/bar/'
        self.iron.mkdir(remote_path)
        self.iron.putfile(self.testdata, remote_path)
        self.iron.lsdir(remote_path)
        self.iron.putfile(self.testdata, remote_path)
        self.iron.rmfile('/bar/bin.tar.xz')
        self.iron.lsdir(remote_path)
        self.iron.putfile(self.testdata, remote_path)
        self.iron.lsdir(remote_path)
        self.iron.getfile('/bar/bin.tar.xz', self.tmp_path)
