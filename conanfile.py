from conans import ConanFile, tools, Meson
from conanos.build import config_scheme
import os, shutil

class GstrtspserverConan(ConanFile):
    name = "gst-rtsp-server"
    version = "1.14.4"
    description = "RTSP server based on GStreamer "
    url = "https://github.com/conanos/gst-rtsp-server"
    homepage = "https://github.com/GStreamer/gst-rtsp-server"
    license = "LGPL-v2"
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("gstreamer/1.14.4@conanos/stable")
        self.requires.add("gst-plugins-base/1.14.4@conanos/stable")

    def build_requirements(self):
        self.build_requires("glib/2.58.1@conanos/stable")
        self.build_requires("libffi/3.299999@conanos/stable")
        self.build_requires("zlib/1.2.11@conanos/stable")

    def source(self):
        remotes = {'origin': 'https://github.com/GStreamer/gst-rtsp-server.git'}
        extracted_dir = self.name + "-" + self.version
        tools.mkdir(extracted_dir)
        with tools.chdir(extracted_dir):
            self.run('git init')
            for key, val in remotes.items():
                self.run("git remote add %s %s"%(key, val))
            self.run('git fetch --all')
            self.run('git reset --hard %s'%(self.version))
            self.run('git submodule update --init --recursive')
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        deps=["gstreamer","gst-plugins-base","glib","libffi","zlib"]
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in deps ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        #binpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["orc"] ]
        meson = Meson(self)
        if self.settings.os == 'Windows':
                meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                                pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

