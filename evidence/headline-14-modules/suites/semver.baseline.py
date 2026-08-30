import pytest
import semver
import sys
import warnings
import collections

# Helper for deprecated warnings
def assert_deprecated(func, *args, **kwargs):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = func(*args, **kwargs)
        assert any(issubclass(wi.category, DeprecationWarning) for wi in w)
        return result

def test_versioninfo_init_and_properties():
    v = semver.VersionInfo(1, 2, 3, "alpha", "build.1")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.prerelease == "alpha"
    assert v.build == "build.1"

    # Test readonly properties
    for attr in ["major", "minor", "patch", "prerelease", "build"]:
        with pytest.raises(AttributeError):
            setattr(v, attr, 10)

def test_versioninfo_negative_values():
    with pytest.raises(ValueError):
        semver.VersionInfo(-1, 0, 0)
    with pytest.raises(ValueError):
        semver.VersionInfo(0, -1, 0)
    with pytest.raises(ValueError):
        semver.VersionInfo(0, 0, -1)

def test_versioninfo_to_tuple_and_to_dict():
    v = semver.VersionInfo(5, 3, 1)
    assert v.to_tuple() == (5, 3, 1, None, None)
    d = v.to_dict()
    assert isinstance(d, collections.OrderedDict)
    assert d["major"] == 5
    assert d["minor"] == 3
    assert d["patch"] == 1
    assert d["prerelease"] is None
    assert d["build"] is None

def test_versioninfo_iter():
    v = semver.VersionInfo(1, 2, 3, "rc.1", "build.2")
    assert tuple(v) == (1, 2, 3, "rc.1", "build.2")

def test_versioninfo_increment_string():
    inc = semver.VersionInfo._increment_string
    assert inc("rc.1") == "rc.2"
    assert inc("foo.9") == "foo.10"
    assert inc("foo") == "foo"
    assert inc("1.2.3") == "1.2.4"
    assert inc("bar.099") == "bar.100"
    assert inc("") == ""

def test_versioninfo_bump_major_minor_patch():
    v = semver.VersionInfo(3, 4, 5)
    assert v.bump_major() == semver.VersionInfo(4, 0, 0)
    assert v.bump_minor() == semver.VersionInfo(3, 5, 0)
    assert v.bump_patch() == semver.VersionInfo(3, 4, 6)

def test_versioninfo_bump_prerelease_and_build():
    v = semver.VersionInfo(3, 4, 5, "rc.1", "build.9")
    assert v.bump_prerelease() == semver.VersionInfo(3, 4, 5, "rc.2")
    assert v.bump_build() == semver.VersionInfo(3, 4, 5, "rc.1", "build.10")

    # If no prerelease/build, should start with token
    v2 = semver.VersionInfo(1, 2, 3)
    assert v2.bump_prerelease() == semver.VersionInfo(1, 2, 3, "rc.1")
    assert v2.bump_prerelease("dev") == semver.VersionInfo(1, 2, 3, "dev.1")
    assert v2.bump_build() == semver.VersionInfo(1, 2, 3, None, "build.1")
    assert v2.bump_build("meta") == semver.VersionInfo(1, 2, 3, None, "meta.1")

def test_versioninfo_compare_and_comparators():
    v1 = semver.VersionInfo(1, 0, 0)
    v2 = semver.VersionInfo(2, 0, 0)
    v3 = semver.VersionInfo(1, 0, 0, "rc.1")
    assert v1.compare(v2) < 0
    assert v2.compare(v1) > 0
    assert v1.compare(v1) == 0
    assert v1 == "1.0.0"
    assert v1 == {"major": 1, "minor": 0, "patch": 0}
    assert v1 == (1, 0, 0)
    assert v1 != v2
    assert v1 < v2
    assert v2 > v1
    assert v1 <= v2
    assert v2 >= v1
    assert v1 >= v1
    assert v1 <= v1
    # prerelease comparison
    assert v1 > v3
    assert v3 < v1

def test_versioninfo_compare_typeerror():
    v = semver.VersionInfo(1, 2, 3)
    with pytest.raises(TypeError):
        v.compare(object())

def test_versioninfo_next_version():
    v = semver.VersionInfo(0, 1, 4)
    assert str(v.next_version("prerelease")) == "0.1.5-rc.1"
    assert v.next_version("major") == v.bump_major()
    assert v.next_version("minor") == v.bump_minor()
    assert v.next_version("patch") == v.bump_patch()
    # Remove prerelease/build if present and bump patch
    v2 = semver.VersionInfo(1, 2, 3, "rc.1", "build.1")
    assert v2.next_version("patch") == v2.replace(prerelease=None, build=None)
    # Invalid part
    with pytest.raises(ValueError):
        v.next_version("foo")

def test_versioninfo_getitem():
    v = semver.VersionInfo(3, 4, 5, "rc.1", "build.2")
    assert v[0] == 3
    assert v[1] == 4
    assert v[2] == 5
    assert v[0:3] == (3, 4, 5)
    # Out of range
    with pytest.raises(IndexError):
        _ = v[10]
    # Negative index
    with pytest.raises(IndexError):
        _ = v[-1]
    # Slicing with negative
    with pytest.raises(IndexError):
        _ = v[-2:3]

def test_versioninfo_repr_and_str_and_hash():
    v = semver.VersionInfo(1, 2, 3, "rc.1", "build.2")
    s = repr(v)
    assert "VersionInfo" in s and "major=1" in s
    assert str(v) == "1.2.3-rc.1+build.2"
    assert hash(v) == hash((1, 2, 3, "rc.1"))

def test_versioninfo_finalize_version():
    v = semver.VersionInfo(1, 2, 3, "rc.5")
    v2 = v.finalize_version()
    assert str(v2) == "1.2.3"
    assert v2.prerelease is None
    assert v2.build is None

def test_versioninfo_match():
    v = semver.VersionInfo(2, 0, 0)
    assert v.match(">=1.0.0")
    assert not v.match(">2.0.0")
    assert v.match("==2.0.0")
    assert v.match("!=1.0.0")
    assert v.match("<3.0.0")
    assert v.match("<=2.0.0")
    # Invalid operator
    with pytest.raises(ValueError):
        v.match("~1.0.0")

def test_versioninfo_parse_and_isvalid():
    v = semver.VersionInfo.parse("3.4.5-pre.2+build.4")
    assert v.major == 3
    assert v.minor == 4
    assert v.patch == 5
    assert v.prerelease == "pre.2"
    assert v.build == "build.4"
    assert semver.VersionInfo.isvalid("1.2.3")
    assert not semver.VersionInfo.isvalid("not.a.version")
    with pytest.raises(ValueError):
        semver.VersionInfo.parse("not.a.version")

def test_versioninfo_replace():
    v = semver.VersionInfo(1, 2, 3)
    v2 = v.replace(major=2, patch=10)
    assert v2.major == 2
    assert v2.minor == 2
    assert v2.patch == 10
    # Invalid key
    with pytest.raises(TypeError):
        v.replace(foo=1)

def test_parse_deprecated():
    d = assert_deprecated(semver.parse, "3.4.5-pre.2+build.4")
    assert d["major"] == 3
    assert d["minor"] == 4
    assert d["patch"] == 5
    assert d["prerelease"] == "pre.2"
    assert d["build"] == "build.4"

def test_parse_version_info_deprecated():
    v = assert_deprecated(semver.parse_version_info, "3.4.5-pre.2+build.4")
    assert isinstance(v, semver.VersionInfo)
    assert v.major == 3

def test_compare_deprecated():
    assert assert_deprecated(semver.compare, "1.0.0", "2.0.0") == -1
    assert assert_deprecated(semver.compare, "2.0.0", "1.0.0") == 1
    assert assert_deprecated(semver.compare, "2.0.0", "2.0.0") == 0

def test_match_deprecated():
    assert assert_deprecated(semver.match, "2.0.0", ">=1.0.0") is True
    assert assert_deprecated(semver.match, "1.0.0", ">1.0.0") is False

def test_max_ver_min_ver_deprecated():
    assert assert_deprecated(semver.max_ver, "1.0.0", "2.0.0") == "2.0.0"
    assert assert_deprecated(semver.min_ver, "1.0.0", "2.0.0") == "1.0.0"
    # max_ver with non-string, non-VersionInfo
    with pytest.raises(TypeError):
        assert_deprecated(semver.max_ver, 123, "2.0.0")

def test_format_version_deprecated():
    s = assert_deprecated(semver.format_version, 3, 4, 5, "pre.2", "build.4")
    assert s == "3.4.5-pre.2+build.4"

def test_bump_major_minor_patch_deprecated():
    assert assert_deprecated(semver.bump_major, "3.4.5") == "4.0.0"
    assert assert_deprecated(semver.bump_minor, "3.4.5") == "3.5.0"
    assert assert_deprecated(semver.bump_patch, "3.4.5") == "3.4.6"

def test_bump_prerelease_build_deprecated():
    assert assert_deprecated(semver.bump_prerelease, "3.4.5", "dev") == "3.4.5-dev.1"
    assert assert_deprecated(semver.bump_build, "3.4.5-rc.1+build.9") == "3.4.5-rc.1+build.10"

def test_finalize_version_deprecated():
    assert assert_deprecated(semver.finalize_version, "1.2.3-rc.5") == "1.2.3"

def test_replace_deprecated():
    assert assert_deprecated(semver.replace, "1.2.3", major=2, patch=10) == "2.2.10"
    with pytest.raises(TypeError):
        assert_deprecated(semver.replace, "1.2.3", foo=1)

def test_astuple_asdict_deprecated():
    v = semver.VersionInfo(1, 2, 3)
    assert assert_deprecated(v._astuple) == (1, 2, 3, None, None)
    d = assert_deprecated(v._asdict)
    assert isinstance(d, collections.OrderedDict)
    assert d["major"] == 1

def test__nat_cmp():
    # a < b
    assert semver._nat_cmp("rc.1", "rc.2") < 0
    # a > b
    assert semver._nat_cmp("rc.2", "rc.1") > 0
    # a == b
    assert semver._nat_cmp("rc.1", "rc.1") == 0
    # int vs str
    assert semver._nat_cmp("1", "alpha") < 0
    assert semver._nat_cmp("alpha", "1") > 0
    # None vs string
    assert semver._nat_cmp(None, "rc.1") < 0
    assert semver._nat_cmp("rc.1", None) > 0
    # Both None
    assert semver._nat_cmp(None, None) == 0

def test_ensure_str():
    # Should work for str and bytes
    s = "abc"
    assert semver.ensure_str(s) == "abc"
    if sys.version_info[0] == 3:
        b = b"abc"
        assert semver.ensure_str(b) == "abc"
    # Not a string
    with pytest.raises(TypeError):
        semver.ensure_str(123)

def test_deprecated_decorator_partial():
    # Should return a partial if func is None
    dec = semver.deprecated(replace="foo", version="1.0.0")
    def f(): pass
    wrapped = dec(f)
    assert callable(wrapped)

def test_cmd_bump():
    class Args:
        def __init__(self, bump, version):
            self.bump = bump
            self.version = version
            self.parser = semver.createparser()
    for part, expected in [
        ("major", "4.0.0"),
        ("minor", "3.5.0"),
        ("patch", "3.4.6"),
        ("prerelease", "3.4.5-rc.1"),
        ("build", "3.4.5+build.1"),
    ]:
        args = Args(part, "3.4.5")
        if part == "prerelease":
            args.version = "3.4.5"
        elif part == "build":
            args.version = "3.4.5"
        assert semver.cmd_bump(args) == expected

def test_cmd_check():
    class Args:
        def __init__(self, version):
            self.version = version
            self.parser = semver.createparser()
    args = Args("1.2.3")
    assert semver.cmd_check(args) is None
    args = Args("not.a.version")
    with pytest.raises(ValueError):
        semver.cmd_check(args)

def test_cmd_compare():
    class Args:
        def __init__(self, v1, v2):
            self.version1 = v1
            self.version2 = v2
            self.parser = semver.createparser()
    args = Args("1.0.0", "2.0.0")
    assert semver.cmd_compare(args) == "-1"

def test_cmd_nextver():
    class Args:
        def __init__(self, version, part):
            self.version = version
            self.part = part
            self.parser = semver.createparser()
    args = Args("0.1.4", "prerelease")
    assert semver.cmd_nextver(args) == "0.1.5-rc.1"

def test_createparser_and_process(monkeypatch):
    parser = semver.createparser()
    # Simulate CLI: bump major 1.2.3
    args = parser.parse_args(["bump", "major", "1.2.3"])
    args.parser = parser
    assert semver.process(args) == "2.0.0"
    # No func attribute
    class DummyArgs:
        def __init__(self):
            self.parser = parser
    with pytest.raises(SystemExit):
        semver.process(DummyArgs())

def test_main_success_and_error(monkeypatch, capsys):
    # Success
    rc = semver.main(["bump", "major", "1.2.3"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "2.0.0" in out
    # Error: invalid version
    rc = semver.main(["check", "not.a.version"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "ERROR" in err

def test_main_no_args(monkeypatch):
    # Should print help and exit
    with pytest.raises(SystemExit):
        semver.main([])

