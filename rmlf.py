#!/usr/bin/python3

'''
* Remove LF(line feed) at the end of comments in Coq files
  These two lines
    | mathematical intuition: If a procedure or method has no side
    | effects, 
  become one line like below.
    | mathematical intuition: If a procedure or method has no side effects, 

* Don't remove LF from lines ending with '.', '|', ':', "#"

* Remove left margin
  Following block
    |      #####################################################
    |      ###  PLEASE DO NOT DISTRIBUTE SOLUTIONS PUBLICLY  ###
    |      #####################################################
  becomes
    |#####################################################
    |###  PLEASE DO NOT DISTRIBUTE SOLUTIONS PUBLICLY  ###
    |#####################################################

* Insert '\n' in front of ankers (-)

* For nahas_tutorial.v, keep code snipets between '<<' and '>>' intact.
    |<<
    |   code
    |>> 

'''

import sys
import os
import re
from pathlib import Path


def fix_comment(fp):
    if (not fp.is_file()) or (not fp.name.lower().endswith('.v')):
        return None

    print("\n --- File: "+fp.name)

    with fp.open() as t:
        ts = t.readlines()

        result = []
        cmt = False
        code = False
        for tl in ts:
            ics = tl.find('(*')
            ice = tl.find('*)')
            print("\n\n------------------ New Line -----------------------")
            print("@@ tl: "+tl)
            print("ics: ", ics)
            print("ice: ", ice)
            if cmt == False:
                if ics == -1:
                    result.append(tl)
                elif ics == 0 and ice > 0:  # single line comment
                    result.append(tl)
                elif ics == 0 and ice == -1:
                    # Don't remove LF from lines ending with '.', '|', ':', "#" or starting with '(**'
                    if re.search(r"[\.|:#] *$", tl) or re.search(r"^\(\*\* *", tl):
                        result.append(tl)
                    else:
                        # remove spaces and LF at the end of a comment line
                        tl2 = re.sub(r" *\n$", " ", tl)
                        result.append(tl2)
                    cmt = True
                else:
                    print("****** Edge case: ics:", ics, " ice:", ice)
            else:
                if re.search(r"^<< *", tl):
                    code = True
                elif re.search(r"^>> *", tl):
                    code = False

                if ice == -1:
                    print("Inside a comment block(ice==-1)")
                    if not (re.search(r"\w", tl) or re.search(r"^ +#+", tl)):  # empty line
                        print("Append an empty line")
                        # insert \n before empty line in case previous line doesn't end with 0x0a
                        if not (len(result) > 0 and len(result[-1]) > 0 and result[-1][-1] != 0x0a):
                            print("result[-1]: ", result[-1])
                            result.append("\n")
                        result.append(tl)
                    else:
                        if re.search(r"^ *-", tl):  # anker list
                            result.append('\n')

                        if code == False:
                            tl2 = re.sub(r"^ +", "", tl)  # remove left margin
                        else:
                            tl2 = tl

                        # Don't remove LF from lines ending with '.', '|', ':', "#"
                        if re.search(r"[\.|:#] *$", tl2) or code == True:
                            result.append(tl2)
                        else:
                            # remove spaces and LF at the end of a comment line
                            tl2 = re.sub(r" *\n$", " ", tl2)
                            result.append(tl2)
                else:
                    print("Comment closing line(ice!=-1)")
                    if code == True:
                        # remove left margin spaces
                        tl = re.sub(r"^ +", "", tl)
                    result.append(tl)
                    cmt = False
                    code = False
        print(result)
        fp2 = Path(fp.parent/(fp.name[:-2]+'_nolf'+fp.name[-2:]))
        with fp2.open('w') as tw:
            tw.write(''.join(result))


def fix_comment_dir(bp):
    if not bp.is_dir():
        fix_comment(bp)
    else:
        print("\n ###### Folder: "+bp.name+" ######")
        for e in bp.iterdir():
            if e.is_dir():
                fix_comment_dir(e)
            else:
                fix_comment(e)


def main():
    args = sys.argv[1:]
    print(args)

    bp = Path(args[0])
    fix_comment_dir(bp)


if __name__ == '__main__':
    main()
