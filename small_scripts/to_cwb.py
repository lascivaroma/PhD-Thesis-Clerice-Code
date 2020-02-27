import glob
import lxml.etree as ET
import regex


hard_punct = regex.compile(r"^[?\.!]+$")

corpus = ET.Element("corpus")
new_tree = ET.ElementTree(corpus)

texts = {

}

with open("./cqp_format.xsl") as f:
    xsl_xml = ET.parse(f)

transform = ET.XSLT(xsl_xml)

for file in list(glob.glob("../aligned_texts/*.xml")):
    with open(file) as f:
        xml = ET.parse(f)

    text_id = xml.getroot().attrib["id"]
    if text_id in texts:
        root = texts[text_id]
    else:
        root = texts[text_id] = ET.Element("text", attrib={"id": text_id})

    sentence = None
    sentence_id = 1
    for token in xml.xpath(".//token"):
        if sentence is None:
            sentence = ET.Element("s", attrib={"id": token.attrib["id"]+"@"+str(sentence_id)})
            sentence_id += 1

        sentence.append(token)

        # New token ? Append sentence and reset for next token
        if sentence is not None and hard_punct.match(token.text.strip()):
            root.append(sentence)
            sentence = None

    if sentence is not None:
        root.append(sentence)


for file in texts:
    with open("corpus/{}.xml".format(file), "w") as f:
        f.write(ET.tostring(texts[file], encoding=str))
    with open("corpus_cqp/{}.vrt".format(file), "w") as f:
        f.write(str(transform(texts[file])))  # Remove XML declaration
        print(file)
