import sys, zipfile, xml.dom.minidom, scribus

def parseStyles ( styles ):
    result = {}
    for s in styles:
        name = s.getAttribute("style:name")

        textPropertiesNode = s.getElementsByTagName("style:text-properties")
        if textPropertiesNode:
            textProperties = textPropertiesNode[0]
            bold = textProperties.getAttribute("fo:font-weight") == "bold"
            italic = textProperties.getAttribute("fo:font-style") == "italic"
            if bold and italic:
                result[name] = '{{{bold-italic}}}'
            elif bold:
                result[name] = '{{{bold}}}'
            elif italic:
                result[name] = '{{{italic}}}'
    return result

def mergeStyles (style1, style2):
    if style1 == '{{{bold-italic}}}' or style2 == '{{{bold-italic}}}':
	return '{{{bold-italic}}}'
    elif style1 == '{{{bold}}}' and style2 == '{{{italic}}}':
	return '{{{bold-italic}}}'
    elif style1 == '{{{italic}}}' and style2 == '{{{bold}}}':
	return '{{{bold-italic}}}'
    elif style1 == '':
	return style2
    elif style2 == '':
	return style1
    return style1

def parseNode( node, styles, previousStyle ):
    result = u''
    nodeStyle = node.getAttribute("text:style-name")
    currentStyle = ''
    if nodeStyle:
        result += previousStyle
        if nodeStyle in styles: currentStyle = mergeStyles(styles[nodeStyle], previousStyle)
        result += currentStyle

    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            result += child.nodeValue
        elif child.nodeType == xml.dom.Node.ELEMENT_NODE:
            result += parseNode( child, styles, currentStyle )
            if child.tagName in ['text:p','text:list','text:h', 'text:line-break']:
                result += "\n"

    if nodeStyle: result += currentStyle + previousStyle
    return result

def mergeDictionaries( a, b):
    result = a.copy()
    result.update(b)
    return result

def parse(filepath):
    zip = zipfile.ZipFile(filepath)
    stylesXml =  xml.dom.minidom.parseString(zip.read("styles.xml"))
    contentXml = xml.dom.minidom.parseString(zip.read("content.xml"))
    styles = mergeDictionaries(
        parseStyles(contentXml.getElementsByTagName("style:style")),
        parseStyles(stylesXml.getElementsByTagName("style:style")))
    return parseNode(contentXml.getElementsByTagName("office:text")[0], styles, '')

def removeEmptyStrings( input ) :
    result=[]
    for line in lines(input):
        if detag(line).strip():
            result.append(line.strip())
    return glue(result)

def header ( text ):
    return lines(text)[0]

def body ( text ):
    l = lines(text)
    return glue(l[1:-2])

def authorName ( text ):
    l = lines(text)
    return l[len(l)-2]

def authorEmail ( text ): 
    l = lines( text )
    return l[len(l)-1]

def glue( lines ) : return '\n'.join(lines)
def lines ( text ) : return text.split('\n')

def detag( text ):
    return text.replace("{{{bold}}}","").replace("{{{bold-italic}}}","").replace("{{{italic}}}","")

def extractModifiers( text ):
    result = []
    detagedPosition = 0
    prevPosition = 0
    while text.find("{{{", prevPosition) > -1:
        position = text.find("{{{", prevPosition)
        detagedPosition += position - prevPosition
        tagedTextStart = text.find("}}}", position) + 3
        tag = text[position+3:tagedTextStart-3]
        tagedTextEnd = text.find("{{{", tagedTextStart)
        tagedTextLen = tagedTextEnd - tagedTextStart
        prevPosition = text.find("}}}", tagedTextEnd) + 3
        if tagedTextLen > 0: 
            result.append({'tag':tag, 'start' : detagedPosition, 'length' : tagedTextLen})
        detagedPosition+= tagedTextLen
    return result

def getX( pageNumber ):
    if pageNumber % 2 == 0:
        return 50
    return 40

if __name__ == "__main__":

    x = getX(scribus.currentPage())

    headerText = scribus.createText(x, 80, 750, 30)
    headerUnderline = scribus.createLine(x, 110, 160, 110)
    bodyText = scribus.createText(x, 120, 750, 1030)
    scribus.setColumns(4, bodyText)
    scribus.setColumnGap(10, bodyText)
    
    if scribus.getObjectType( bodyText ) == "TextFrame":
        fileName = scribus.fileDialog("Open odt file", 'ODT files (*.odt)')
        text = removeEmptyStrings(parse(fileName))
        header = detag(header(text));
        body = body(text);

        scribus.deleteText( bodyText )
        scribus.insertText(lines(detag(body))[0], -1, bodyText)
        scribus.setStyle("first_paragraph", bodyText)
        
        for p in lines(detag(body))[1:]:
            scribus.insertText("\n"+p, -1, bodyText)
            scribus.setStyle("eot", bodyText)
        for tag in extractModifiers( body ):
            scribus.selectText(tag['start'], tag['length'], bodyText)
            if tag['tag'] == "bold":
                scribus.setFont("Mysl Bold Cyrillic", bodyText)
            elif tag['tag'] == "italic":
                scribus.setFont("Mysl Italic Cyrillic", bodyText)
            else:
                scribus.setFont("Mysl BoldItalic Cyrillic", bodyText)

        scribus.insertText("\n"+authorName(detag(text)), -1, bodyText)
        scribus.setStyle("author name", bodyText)

        scribus.insertText("\n"+authorEmail(detag(text)), -1, bodyText)
        scribus.setStyle("author emali", bodyText)

        scribus.hyphenateText(bodyText)

        scribus.insertText(header, -1, headerText)
        scribus.setStyle("article header", headerText)


    else: scribus.messageBox("error", "select text frame")

