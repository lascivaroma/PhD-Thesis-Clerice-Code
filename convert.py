import lxml.etree as ET
import glob
from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver


CORPORA_PATH = "data/raw/corpora/**/*"
repositories = list(glob.glob(CORPORA_PATH, recursive=False))
resolver = CtsCapitainsLocalResolver(repositories)


sys.exit()
xsl = ET.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs" xmlns:tei="http://www.tei-c.org/ns/1.0"
    version="1.0">
    <xsl:output method="text" encoding="UTF-8"/>
    <xsl:template match="tei:note">
        <xsl:text> </xsl:text>
    </xsl:template>
    <xsl:template match="tei:p|tei:div|tei:seg|tei:l|tei:w|tei:ab">
        <xsl:param name="previous" />
        <xsl:text> </xsl:text><xsl:apply-templates ><xsl:with-param name="previous" select="$previous" /></xsl:apply-templates>
    </xsl:template>
    <xsl:template match="tei:teiHeader|tei:label|tei:ref|tei:milestone|tei:orig|tei:abbr|tei:head|tei:title|tei:teiHeader|tei:del|tei:g|tei:bibl|tei:front|tei:back|tei:foreign" />
    {previous}
</xsl:stylesheet>""".format(previous=data))

"""    <xsl:template match="/tei:TEI/tei:text/tei:body//tei:div[@n]">
        [REF_type1:<xsl:value-of select="@n"/>]
        <xsl:apply-templates>
            <xsl:with-param name="previous"><xsl:value-of select="@n"/></xsl:with-param>
        </xsl:apply-templates>
    </xsl:template>
    <xsl:template match="/tei:TEI/tei:text/tei:body/tei:div[@n]/tei:div[@n]">
        <xsl:param name="previous" />
        <xsl:message><xsl:value-of select="$previous"/></xsl:message>
        [REF_type2:<xsl:value-of select="$previous" />.<xsl:value-of select="@n"/>]
        <xsl:apply-templates>
            <xsl:with-param name="previous"><xsl:value-of select="$previous" />.<xsl:value-of select="@n"/></xsl:with-param>
        </xsl:apply-templates>
    </xsl:template>
    <xsl:template match="/tei:TEI/tei:text/tei:body/tei:div[@n]/tei:div[@n]//tei:ab[@n]">
        <xsl:param name="previous" />
        [REF_type3:<xsl:value-of select="$previous" />.<xsl:value-of select="@n"/>]
        <xsl:apply-templates />
    </xsl:template>"""