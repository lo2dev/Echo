desktop_file = i18n.merge_file(
        input: 'io.github.lo2dev.Echo.desktop.in',
       output: 'io.github.lo2dev.Echo.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'io.github.lo2dev.Echo.metainfo.xml.in',
       output: 'io.github.lo2dev.Echo.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data('io.github.lo2dev.Echo.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])

subdir('icons')

configure_file(
  input: 'io.github.lo2dev.Echo.service',
  output: '@0@.service'.format(app_id),
  configuration: { 'app_id': app_id, 'bindir': bindir },
  install: true,
  install_dir: join_paths(get_option('datadir'), 'dbus-1/services')
)
