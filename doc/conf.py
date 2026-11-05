# Sphinx configuration for the Pass documentation.
project = 'Pass'
author = 'Rim Valiulin'
copyright = '2012-2026, Rim Valiulin'

release = __import__('Pass').get_version()
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

templates_path = ['_templates']
exclude_patterns = ['_build', 'requirements.txt']

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
}
