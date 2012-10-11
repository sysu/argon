from distutils.core import setup, Extension
setup(name = "ext_user",
        version = "1.0",
        maintainer = "",
        maintainer_email = "",
        description = "Argo ext_user module",
        ext_modules = [Extension('ext_user',
            sources=['user.c'],
            extra_compile_args=['-m32'],
            extra_link_args=['-m32'])
            ]
        )

