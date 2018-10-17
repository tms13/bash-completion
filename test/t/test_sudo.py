import pytest

from conftest import assert_complete


class TestSudo:

    @pytest.mark.complete("sudo -")
    def test_1(self, completion):
        assert completion.list

    @pytest.mark.complete("sudo cd fo", cwd="shared/default")
    def test_2(self, completion):
        assert completion.list == ["foo.d/"]
        assert not completion.line.endswith(" ")

    @pytest.mark.complete("sudo sh share")
    def test_3(self, completion):
        assert completion.list == ["shared/"]
        assert not completion.line.endswith(" ")

    @pytest.mark.complete("sudo mount /dev/sda1 def", cwd="shared")
    def test_4(self, completion):
        assert completion.list == ["default/"]
        assert not completion.line.endswith(" ")

    @pytest.mark.complete("sudo -e -u root bar foo", cwd="shared/default")
    def test_5(self, completion):
        assert completion.list == ["foo", "foo.d/"]

    def test_6(self, bash, part_full_user):
        part, full = part_full_user
        completion = assert_complete(bash, "sudo chown %s" % part)
        assert completion.list == [full]
        assert completion.line.endswith(" ")

    def test_7(self, bash, part_full_user, part_full_group):
        _, user = part_full_user
        partgroup, fullgroup = part_full_group
        completion = assert_complete(
            bash, "sudo chown %s:%s" % (user, partgroup))
        assert completion.list == ["%s:%s" % (user, fullgroup)]
        assert completion.line.endswith(" ")

    def test_8(self, bash, part_full_group):
        part, full = part_full_group
        completion = assert_complete(bash, "sudo chown dot.user:%s" % part)
        assert completion.list == ["dot.user:%s" % full]
        assert completion.line.endswith(" ")

    @pytest.mark.xfail  # TODO check escaping, whitespace
    def test_9(self, bash, part_full_group):
        """Test preserving special chars in $prefix$partgroup<TAB>."""
        part, full = part_full_group
        for prefix in (r"funky\ user:", "funky.user:", r"funky\.user:",
                       r"fu\ nky.user:", r"f\ o\ o\.\bar:",
                       r"foo\_b\ a\.r\ :"):
            completion = assert_complete(
                bash, "sudo chown %s%s" % (prefix, part))
            assert completion.list == ["%s%s" % (prefix, full)]
            assert completion.line.endswith(" ")

    def test_10(self, bash, part_full_user, part_full_group):
        """Test giving up on degenerate cases instead of spewing junk."""
        _, user = part_full_user
        partgroup, _ = part_full_group
        for x in range(2, 5):
            completion = assert_complete(
                bash, "sudo chown %s%s:%s" % (user, x * "\\", partgroup))
            assert not completion.list

    def test_11(self, bash, part_full_group):
        """Test graceful fail on colon in user/group name."""
        part, _ = part_full_group
        completion = assert_complete(bash, "sudo chown foo:bar:%s" % part)
        assert not completion.list
