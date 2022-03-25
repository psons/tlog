#!/usr/local/bin/python3
import os
import unittest

import testdata
import unit_test_tmp_dir

import journaldir
import tlog

#.tlog import write_back_updated_story

from docsec import Section, TLogInternalException, ItemAttribute, Item
from testdata import dtask_line, dtask_item_text, \
    as1, vs1, as2, vs2, ai1, vi1, item_attrib_line1, ai2, vi2, item_attrib_line2, item_2attr_str, \
    dtask_item_text_w_saved_hash, dtask_item_text_w_saved_hash_modified_title, sec_two_items, sec_attrib_wrong, \
    sec_w_attrib, sec_head, is_attrib_section_cases
from tldocument import TLDocument
import tldocument


class TestItem(unittest.TestCase):

    def testNoneNull(self):
        self.assertEqual(str(Item(tldocument.top_parser_pat, None)), "")

    def testEmptyItemTrue(self):
        self.assertTrue(Item(tldocument.top_parser_pat).is_empty())

    def testEmptyTopItemFalse(self):
        self.assertFalse(Item(tldocument.top_parser_pat, "d - somthing").is_empty())

    def testEmptySubItemFalse(self):
        self.assertFalse(Item(tldocument.top_parser_pat, " - sub line").is_empty())

    def testEmptyAttribItemFalse(self):
        self.assertFalse(Item(tldocument.top_parser_pat, "a: v").is_empty())

    def testSubItem(self):
        "Item with just sub text look ok?"
        txt = "free text"
        itest: Item = Item(tldocument.top_parser_pat, txt)
        self.assertEqual(str(itest), txt)

    def testItemWithList(self):
        out = """\
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
        itest: Item = Item(tldocument.top_parser_pat, "d - do somthing")
        itest.add_item_line(" - sub item list item 1")
        itest.add_item_line(" - sub item list item 2")
        itest.add_item_line("free text")
        self.assertEqual(str(itest), out)

    def testFullBlownItem(self):
        "A full blown item can be created from text and converted back to the same string."
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_item_text)
        self.assertEqual(str(itest), dtask_item_text)

    def testItemDeepCopyDifferentObject(self):
        "Does item.deep_copy() return an item with a different id?"
        itest: Item = Item(tldocument.top_parser_pat, "d - do somthing")
        itest1 = itest.deep_copy(tldocument.top_parser_pat)
        self.assertNotEqual(id(itest), id(itest1))

    def testItemDeepCopyEqual(self):
        "Does item.deep_copy() return a same string item?"
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_item_text)
        itest1 = itest.deep_copy(tldocument.top_parser_pat)
        self.assertEqual(str(itest), str(itest1))

    def testGetItemTitle1(self):
        """get_title() base case with leader and title"""
        leader = "d -"
        title_in = "item with no sub lines!"
        itest: Item = Item(tldocument.top_parser_pat, "{}{}".format(leader, title_in))
        title_out = itest.get_title()
        # print("x{}x".format(itest.top))
        # print("title_in:{} title_out:{}".format(title_in, title_out))
        self.assertEqual(title_in, title_out)

    def testGetItemTitle2(self):
        """get_title() with trailing whitespace to ignore in title"""
        leader = "d -"
        title_in = "item with no sub lines!"
        itest: Item = Item(tldocument.top_parser_pat, "{} {} ".format(leader, title_in))  # trailing white space
        title_out = itest.get_title()
        # print("x{}x".format(itest.top))
        # print("title_in:{} title_out:{}".format(title_in, title_out))
        self.assertEqual(title_in, title_out)

    def testGetItemTitle3(self):
        """get_title() with leading white space to ignore in title"""
        leader = "d -"
        title_in = "item with no sub lines!"
        itest: Item = Item(tldocument.top_parser_pat, "{} {} ".format(leader, title_in))  # leading white space
        title_out = itest.get_title()
        # print("x{}x".format(itest.top))
        # print("title_in:{} title_out:{}".format(title_in, title_out))
        self.assertEqual(title_in, title_out)

    def testGetItemTitle4(self):
        """get_title() with only white space in title"""
        leader = "d -"
        title_in = ""
        expected = None
        itest: Item = Item(tldocument.top_parser_pat, "{}{} ".format(leader, title_in))
        title_out = itest.get_title()
        # print("x{}x".format(itest.top))
        # print("title_in:{} title_out:{} expected:{}".format(
        # 	title_in, title_out, expected))
        self.assertEqual(expected, title_out)

    def testGetItemTitleHash1(self):
        """Base case"""
        leader = "d -"
        title_in = "item with no sub lines!"
        itest: Item = Item(tldocument.top_parser_pat, "{} {} ".format(leader, title_in))  # leading white space
        t_hash = itest.get_title_hash()
        self.assertEqual(t_hash, 'f3ebd9014f')

    def testGetItemTitleHash2(self):
        """empty title should return empty string for hash"""
        leader = "d -"
        title_in = ""
        itest: Item = Item(tldocument.top_parser_pat, "{} {} ".format(leader, title_in))  # leading white space
        t_hash = itest.get_title_hash()
        self.assertEqual('', t_hash)

    def testSaveItemTitleHash1(self):
        """Saved title hash matches expected"""
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_item_text)
        itest.save_title_hash()
        saved_hash = itest.get_saved_title_hash()
        # print("itest:\n", itest)
        # print("dtask_item_text_w_saved_hash:" + dtask_item_text_w_saved_hash)
        self.assertEqual('9b35f4f8b4', saved_hash)

    def testSaveItemModifiedTitleHash1(self):
        """
		Saved title hash with modified title is detectable
		Simulates detection of when a user has modified a task title that came in
		from a story file
		"""
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_item_text_w_saved_hash_modified_title)
        # hash is in the saved input
        # print("itest:\n", itest)
        # print("dtask_item_text_w_saved_hash (unmodified) :" + dtask_item_text_w_saved_hash)
        self.assertEqual(False, itest.title_matches_hash())

    def testSaveItemUnModifiedTitleHash1(self):
        """
		Saved title hash with modified title is detectable
		Simulates detection of when a user has modified a task title that came in
		from a story file
		"""
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_item_text_w_saved_hash)
        # hash is in the saved input
        # print(itest.get_title_hash())
        # print("itest:\n", itest)
        # print("dtask_item_text_w_saved_hash (unmodified) :\n" + dtask_item_text_w_saved_hash)
        self.assertEqual(True, itest.title_matches_hash())

    def testAddMissingTitleHashAddsHash(self):
        """
        given an Item with a top line and no saved titleHash
        when add_missing_title_hash() is called
        then a title hash will be present.
        """
        itest = Item.fromtext(tldocument.top_parser_pat, dtask_line)
        pre_condition = itest.get_saved_title_hash()
        # print(f"pre_condition: {pre_condition}")
        self.assertEqual(pre_condition, None)
        itest.add_missing_title_hash()
        post_condition = itest.get_saved_title_hash()
        # print(f"post_condition: {post_condition}")
        self.assertEqual('9b35f4f8b4', post_condition)

    def testAddMissingTitleHashIgnoreSavedHash(self):
        """
        given an Item with a top line and a saved titleHash that does not match the actual top line hash
        when add_missing_title_hash() is called
        then the original saved titleHash non-matching title hash will still be present.

        This test is required so that add_missing_title_hash() can be called on any item read from the to do  / journal
        and both cases are handled correctly:
            (1) new item gets a title hash.
            (2) an item with a changed title still has its old hash so it can be matched to update it's original story item
        """
        itest: Item = Item.fromtext(tldocument.top_parser_pat, dtask_item_text_w_saved_hash)
        # print(f'itest: {itest}')
        itest.add_item_line('d - a new topline') # force top line to mismatch the titleHash
        # print(f'itest: {itest}')
        pre_condition = itest.get_saved_title_hash()
        # print(f"pre_condition: {pre_condition}")
        itest.add_missing_title_hash()
        post_condition = itest.get_saved_title_hash()
        # print(f"post_condition: {post_condition}")
        self.assertEqual(pre_condition, post_condition)

    def testItemNoSub(self):
        out = "d - item with no sub lines!"
        itest: Item = Item(tldocument.top_parser_pat, out)
        self.assertEqual(str(itest), out)

    def testItemNoHeader(self):
        out = " - subitem with no item header"
        itest: Item = Item(tldocument.top_parser_pat, None)
        itest.subs.append(out)
        self.assertEqual(str(itest), out)

    def testinProgressPatternSlash(self):
        data = "/ - doing somthing"
        my_bool = tldocument.head_pat.match(data)
        # print(f"my_bool: {my_bool}")
        self.assertIsNotNone(my_bool)

    def testinProgressPatternBackSlash(self):
        data = "\ - doing somthing else"
        self.assertTrue(tldocument.top_parser_pat.match(data))

    def testChange_in_prog_2_unfin(self):
        data = "\ - doing somthing else"
        itest: Item = Item(tldocument.top_parser_pat, data)
        itest.modify_item_top(tldocument.in_progress_pat, tldocument.unfinished_s)
        self.assertTrue(tldocument.unfinished_pat.match(itest.top))

    def testSecHeadToItemRaisesE(self):
        with self.assertRaises(TLogInternalException) as tle:
            an_item: Item = Item(tldocument.top_parser_pat)
            an_item.add_item_line(sec_head)
        part_of_e_val = tle.exception.value[:62]
        # print("part_of_e_val:", part_of_e_val)
        self.assertEqual("Putting a Section.head_pat line inside a Item is not allowed: ", part_of_e_val)

    def testItemSetAttribGetAttribSymmetry(self):
        """Item get_item_attrib / set_doc_attrib symmetry"""
        itest: Item = Item(tldocument.top_parser_pat)
        itest.set_attrib(ai1, vi1)
        self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)

    def testItemGetAttribNone1(self):
        """Item get_item_attrib should return None of the key is not present"""
        itest: Item = Item(tldocument.top_parser_pat)
        self.assertEqual(itest.get_item_attrib(ai1), None)

    def testItemGetAttribNone2(self):
        """Item get_item_attrib should return None of the key is not present"""
        itest: Item = Item(tldocument.top_parser_pat, dtask_line)
        self.assertEqual(itest.get_item_attrib(ai1), None)

    def testItemAttrib(self):
        itest: Item = Item(tldocument.top_parser_pat, item_attrib_line1)
        self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)

    def testItem2Attribs(self):
        itest: Item = Item(tldocument.top_parser_pat, item_attrib_line1)
        itest.add_item_line(item_attrib_line2)
        self.assertEqual(str(itest.get_item_attrib(ai1)), vi1)
        self.assertEqual(str(itest.get_item_attrib(ai2)), vi2)

    def testItem2AttribsStr(self):
        "Does attribs_str work for a 2 attribute Item?"
        itest: Item = Item(tldocument.top_parser_pat, item_attrib_line1)
        itest.add_item_line(item_attrib_line2)
        # print(itest.attribs_str())
        self.assertEqual(item_2attr_str, itest.attribs_str())


class testSection(unittest.TestCase):

    def testEmptySectionTrue(self):
        "Does the is_empty() return true for empty section?"
        self.assertTrue(Section(tldocument.top_parser_pat).is_empty())

    def testEmptySectionHeaderFalse(self):
        "Does the is_empty() return false for section with a heading?"
        s: Section = Section(tldocument.top_parser_pat, "# header")
        ie = s.is_empty()
        self.assertFalse(ie)

    def testEmptySectionItemFalse(self):
        "Does the is_empty() return false for section with an item with a top?"
        self.assertFalse(Section(tldocument.top_parser_pat, "d - task").is_empty())

    def testEmptySectionItemSubFalse(self):
        "Does the is_empty() return false for section with an item with a sub text?"
        self.assertFalse(Section(tldocument.top_parser_pat, " - task detail").is_empty())

    def testSectionWithItem(self):
        out = """\
#Section
d - do somthing
 - sub item list item 1
 - sub item list item 2
free text\
"""
        stest: Section = Section(tldocument.top_parser_pat, "#Section")
        stest.add_section_line("d - do somthing")
        stest.add_section_line(" - sub item list item 1")
        stest.add_section_line(" - sub item list item 2")
        stest.add_section_line("free text")
        self.assertEqual(out, str(stest))

    def testStrItemsList(self):
        out = """\
d - do 1
d - do 2
d - do 3\
"""
        stest: Section = Section(tldocument.top_parser_pat, "d - do 1")
        stest.add_section_line("d - do 2")
        stest.add_section_line("d - do 3")
        self.assertEqual(out, stest.str_body())

    def testStrItemsHead(self):
        out = """\
#  a Header\
"""
        stest: Section = Section(tldocument.top_parser_pat, "#  a Header")
        self.assertEqual(stest.str_body(), "")

    def testStrItemsAttribute(self):
        out = """\
#  a Header
AnAttributeName: the Attribute Value\
"""
        stest: Section = Section(tldocument.top_parser_pat, "#  a Header")
        stest.add_section_line("AnAttributeName: the Attribute Value")
        self.assertEqual(str(stest), out)

    # @unittest.skip("Reworking  testing with a better way to initialize multi line things.")
    def testSectionGetAttributeNone(self):
        "Does Section get_attribute return None if the first Item has a top?"
        stest = Section.fromtext(tldocument.top_parser_pat, sec_attrib_wrong)
        self.assertEqual(stest.get_section_attrib(as1), None)

    def testSectionGetAttribute(self):
        "Does Section get_attribute return the attribute?"
        stest = Section.fromtext(tldocument.top_parser_pat, sec_w_attrib)
        self.assertEqual(vs1, stest.get_section_attrib(as1))

    def testSectionSetAttributeNew(self):
        "Does set_attribute add a new attribute"
        stest: Section = Section(tldocument.top_parser_pat)
        stest.set_sec_attrib(as1, vs1)
        self.assertEqual(vs1, stest.get_section_attrib(as1))

    def testSectionSetAttributeReplace(self):
        "Does set_attribute update an existing attribute?"
        stest = Section.fromtext(tldocument.top_parser_pat, sec_w_attrib)
        stest.set_sec_attrib(as1, vs2)
        self.assertEqual(vs2, stest.get_section_attrib(as1))

    def testSectionSetAttributeAdd(self):
        """
		Does set_attribute add an attribute if a different one 
		already exists?
		"""
        stest = Section.fromtext(tldocument.top_parser_pat, sec_w_attrib)
        stest.set_sec_attrib(as2, vs2)
        self.assertEqual(vs2, stest.get_section_attrib(as2))

    def testSectionSetAttributeWithItem(self):
        """
		Does set_attribute add an attribute if there are Items in the Section? 
		"""
        stest = Section.fromtext(tldocument.top_parser_pat, sec_two_items)
        stest.set_sec_attrib(as2, vs2)
        self.assertEqual(vs2, stest.get_section_attrib(as2))

    def testSectionGetAttributeNotFound(self):
        "Does Section get_attribute for a key that is not present return None?"
        stest = Section.fromtext(tldocument.top_parser_pat, sec_w_attrib)
        self.assertIs(stest.get_section_attrib("wrongKey"), None)

    def testSectionWith2Items(self):
        stest = Section.fromtext(tldocument.top_parser_pat, sec_two_items)
        self.assertEqual(sec_two_items, str(stest))

    def testSectionWithNoBody(self):
        out = """\
#Section with no body_items\
"""
        stest: Section = Section(tldocument.top_parser_pat, "#Section with no body_items")
        self.assertEqual(str(stest), out)

    def testSectionInProgItem(self):
        out = """\
\ - doing somthing else\
"""
        stest: Section = Section(tldocument.top_parser_pat, "\ - doing somthing else")
        self.assertEqual(str(stest), out)

    def testUpdateProgress1(self):
        "test marking in progress as unfinished for \ - "
        data = "\ - one thing going on"
        out = "u - one thing going on"
        itest: Item = Item(tldocument.top_parser_pat, data)
        itest.modify_item_top(tldocument.in_progress_pat, tldocument.unfinished_s)
        self.assertEqual(str(itest), out)

    def testUpdateProgress2(self):
        "test marking in progress as unfinished for / - "
        data = "/ - another thing going on"
        out = "u - another thing going on"
        itest: Item = Item(tldocument.top_parser_pat, data)
        itest.modify_item_top(tldocument.in_progress_pat, tldocument.unfinished_s)
        self.assertEqual(str(itest), out)

    def test_is_attrib_section(self):
        "Does the is_empty() return false for section with an item with a sub text?"
        for case in is_attrib_section_cases:
            input_val = case[0]
            expected = case[1]
            actual = Section.fromtext(tldocument.top_parser_pat, input_val).is_attrib_section()
            # print("input: {} expected: {}, actual: {}".format(input_val, expected, actual))
            self.assertEqual(expected, actual)

    #def test_add_all_missing_item_titleHash(self):


class testTLAttribute(unittest.TestCase):
    positive_key = "SomeAttribute"
    positive_value = " the value of it"
    valid_line = positive_key + ":" + positive_value

    def positive_pattern():
        return ItemAttribute.attr_pat.match(testTLAttribute.valid_line)

    def negitive_pattern():
        data = "SomeAttribute the value of it"
        return ItemAttribute.attr_pat.match(data)

    def testTLAttributePatternMatch(self):
        "Does the recognition pattern return a match object?"
        self.assertTrue(testTLAttribute.positive_pattern())

    def testTLAttributePatternNoMatch(self):
        "Does a pattern mismatch return None?"
        self.assertFalse(testTLAttribute.negitive_pattern())

    def testTLAttributePatternKey(self):
        "Does a pattern match set the key?"

        mo = testTLAttribute.positive_pattern()  # mo is match Object
        testAttr = ItemAttribute(mo.group(1), mo.group(2))

        self.assertEqual(testAttr.name, testTLAttribute.positive_key)
        self.assertEqual(testAttr.value, testTLAttribute.positive_value)

    def testTLAttributeStr(self):
        "str() of a TLAttribute should give the text it was made from"
        self.assertEqual(
            str(ItemAttribute.fromline(testTLAttribute.valid_line)),
            testTLAttribute.valid_line)

class TestStoryIO(unittest.TestCase):
    """prove story reading and writing work flows in docs/Tlog User Documentation.md"""
# load_story_from_file(file_name) should have titleHash and StorySource
# write_back_updated_story(item: Item)

    userPathObject = None


    @classmethod
    def setUpClass(cls):
        cls.userPathObject = testdata.getUnitTestUserPathObject()
        #journaldir.UserPaths(ut_journal_root, ut_tmp_root, ut_endeavor_dir)

    def test_write_item_to_story_file(self):
        # get an item with a storySource attribute
        # write the item
        # read back the item
        # delete the file, maybe make a file scaffolding module.
        fileIOPath = journaldir.path_join(TestStoryIO.userPathObject.endeavor_path, "testGoal")
        fileIOPath = journaldir.path_join(fileIOPath, "testDrivenStory.md")
        new_item_section_heading = "# test_write_item_to_story_file\n"
        journaldir.remove_filepath(fileIOPath)
        # print( f"write_item_to_story_file dtask_item_text: {dtask_item_text}" )
        storyItem = Item.fromtext(tldocument.top_parser_pat, dtask_item_text)
        storyItem.set_attrib("storySource", fileIOPath)
        # print(f"storyItem:\n{storyItem}")
        tlog.write_item_to_story_file(storyItem, new_item_section_head=new_item_section_heading)
        reloadStory: TLDocument = tlog.load_doc_from_file(fileIOPath)
        self.assertEqual(new_item_section_heading + str(storyItem), str(reloadStory))




if __name__ == '__main__':
    # print(doc1_text)
    unittest.main()


