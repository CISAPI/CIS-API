
from distutils.core import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
pypiReadme=path.join(this_directory, 'PYPI-README.md')
long_description=""
if(path.isfile(pypiReadme)):
	with open(pypiReadme, encoding='utf-8') as f:
		long_description = f.read()

setup(
  name = 'cisapi',
  packages = ['cisapi'],
  version = "2021.09.01",
  license='MIT',
  #description = 'Python bindings for the CIS Automotive API.',   # Give a short description about your library
  long_description_content_type="text/html",
  long_description=long_description,
  
  author = 'Competitive Intelligence Solutions LLC',                   # Type in your name
  author_email = 'engineering@competitiveintelligencesolutions.com',      # Type in your E-Mail
  url = 'https://autodealerdata.com',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/CISAPI/CIS-API/archive/refs/tags/2021.09.01.tar.gz',    # I explain this later on
  keywords = ['CIS', 'Automotive', 'API', 'Library'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  python_requires='>=3.6',
)
