import os
import pytest

from buildstream._exceptions import ErrorDomain, LoadErrorReason
from buildstream.plugintestutils import cli

DATA_DIR = os.path.dirname(os.path.realpath(__file__))


#
# Exercising some different ways of loading the dependencies
#
@pytest.mark.datafiles(DATA_DIR)
def test_two_files(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    elements = cli.get_pipeline(project, ['target.bst'])
    assert elements == ['firstdep.bst', 'target.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_shared_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    elements = cli.get_pipeline(project, ['shareddeptarget.bst'])
    assert elements == ['firstdep.bst', 'shareddep.bst', 'shareddeptarget.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_dependency_dict(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')
    elements = cli.get_pipeline(project, ['target-depdict.bst'])
    assert elements == ['firstdep.bst', 'target-depdict.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_invalid_dependency_declaration(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')
    result = cli.run(project=project, args=['show', 'invaliddep.bst'])
    result.assert_main_error(ErrorDomain.LOAD, LoadErrorReason.INVALID_DATA)


@pytest.mark.datafiles(DATA_DIR)
def test_invalid_dependency_type(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')
    result = cli.run(project=project, args=['show', 'invaliddeptype.bst'])
    result.assert_main_error(ErrorDomain.LOAD, LoadErrorReason.INVALID_DATA)


@pytest.mark.datafiles(DATA_DIR)
def test_circular_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')
    result = cli.run(project=project, args=['show', 'circulartarget.bst'])
    result.assert_main_error(ErrorDomain.LOAD, LoadErrorReason.CIRCULAR_DEPENDENCY)


@pytest.mark.datafiles(DATA_DIR)
def test_build_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    elements = cli.get_pipeline(project, ['builddep.bst'], scope='run')
    assert elements == ['builddep.bst']

    elements = cli.get_pipeline(project, ['builddep.bst'], scope='build')
    assert elements == ['firstdep.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_runtime_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')
    elements = cli.get_pipeline(project, ['runtimedep.bst'], scope='build')

    # FIXME: The empty line should probably never happen here when there are no results.
    assert elements == ['']
    elements = cli.get_pipeline(project, ['runtimedep.bst'], scope='run')
    assert elements == ['firstdep.bst', 'runtimedep.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_all_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    elements = cli.get_pipeline(project, ['alldep.bst'], scope='build')
    assert elements == ['firstdep.bst']

    elements = cli.get_pipeline(project, ['alldep.bst'], scope='run')
    assert elements == ['firstdep.bst', 'alldep.bst']


@pytest.mark.datafiles(DATA_DIR)
def test_list_build_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    # Check that the pipeline includes the build dependency
    deps = cli.get_pipeline(project, ['builddep-list.bst'], scope="build")
    assert "firstdep.bst" in deps


@pytest.mark.datafiles(DATA_DIR)
def test_list_runtime_dependency(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    # Check that the pipeline includes the runtime dependency
    deps = cli.get_pipeline(project, ['runtimedep-list.bst'], scope="run")
    assert "firstdep.bst" in deps


@pytest.mark.datafiles(DATA_DIR)
def test_list_dependencies_combined(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    # Check that runtime deps get combined
    rundeps = cli.get_pipeline(project, ['list-combine.bst'], scope="run")
    assert "firstdep.bst" not in rundeps
    assert "seconddep.bst" in rundeps
    assert "thirddep.bst" in rundeps

    # Check that build deps get combined
    builddeps = cli.get_pipeline(project, ['list-combine.bst'], scope="build")
    assert "firstdep.bst" in builddeps
    assert "seconddep.bst" not in builddeps
    assert "thirddep.bst" in builddeps


@pytest.mark.datafiles(DATA_DIR)
def test_list_overlap(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies1')

    # Check that dependencies get merged
    rundeps = cli.get_pipeline(project, ['list-overlap.bst'], scope="run")
    assert "firstdep.bst" in rundeps
    builddeps = cli.get_pipeline(project, ['list-overlap.bst'], scope="build")
    assert "firstdep.bst" in builddeps


#
# Testing the order of elements reported when iterating through
# Element.dependencies() with various scopes.
#
@pytest.mark.datafiles(DATA_DIR)
def test_scope_all(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies2')
    elements = ['target.bst']

    element_list = cli.get_pipeline(project, elements, scope='all')

    assert len(element_list) == 7

    assert element_list[0] == "build-build.bst"
    assert element_list[1] == "run-build.bst"
    assert element_list[2] == "build.bst"
    assert element_list[3] == "dep-one.bst"
    assert element_list[4] == "run.bst"
    assert element_list[5] == "dep-two.bst"
    assert element_list[6] == "target.bst"


@pytest.mark.datafiles(DATA_DIR)
def test_scope_run(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies2')
    elements = ['target.bst']

    element_list = cli.get_pipeline(project, elements, scope='run')

    assert len(element_list) == 4

    assert element_list[0] == "dep-one.bst"
    assert element_list[1] == "run.bst"
    assert element_list[2] == "dep-two.bst"
    assert element_list[3] == "target.bst"


@pytest.mark.datafiles(DATA_DIR)
def test_scope_build(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies2')
    elements = ['target.bst']

    element_list = cli.get_pipeline(project, elements, scope='build')

    assert len(element_list) == 3

    assert element_list[0] == "dep-one.bst"
    assert element_list[1] == "run.bst"
    assert element_list[2] == "dep-two.bst"


@pytest.mark.datafiles(DATA_DIR)
def test_scope_build_of_child(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies2')
    elements = ['target.bst']

    element_list = cli.get_pipeline(project, elements, scope='build')

    # First pass, lets check dep-two
    element = element_list[2]

    # Pass two, let's look at these
    element_list = cli.get_pipeline(project, [element], scope='build')

    assert len(element_list) == 2

    assert element_list[0] == "run-build.bst"
    assert element_list[1] == "build.bst"


@pytest.mark.datafiles(DATA_DIR)
def test_no_recurse(cli, datafiles):
    project = os.path.join(str(datafiles), 'dependencies2')
    elements = ['target.bst']

    # We abuse the 'plan' scope here to ensure that we call
    # element.dependencies() with recurse=False - currently, no `bst
    # show` option does this directly.
    element_list = cli.get_pipeline(project, elements, scope='plan')

    assert len(element_list) == 7

    assert element_list[0] == 'build-build.bst'
    assert element_list[1] in ['build.bst', 'run-build.bst']
    assert element_list[2] in ['build.bst', 'run-build.bst']
    assert element_list[3] in ['dep-one.bst', 'run.bst', 'dep-two.bst']
    assert element_list[4] in ['dep-one.bst', 'run.bst', 'dep-two.bst']
    assert element_list[5] in ['dep-one.bst', 'run.bst', 'dep-two.bst']
    assert element_list[6] == 'target.bst'
