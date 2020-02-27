<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    xmlns:foo="foo"
    version="1.0">
    <xsl:template match="text">
        <xsl:copy>
            <xsl:text>&#xa;</xsl:text>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="s">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:text>&#xa;</xsl:text>
            <xsl:apply-templates select="token"/>
        </xsl:copy>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>
    <xsl:template match="token">
        <xsl:value-of select="./text()"/>
        <xsl:text>&#x9;</xsl:text>
        <xsl:choose>
            <xsl:when test="string-length(@pos) > 0">
                <xsl:value-of select="@pos"/>
            </xsl:when>
            <xsl:otherwise><xsl:text>OUT</xsl:text></xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x9;</xsl:text>
        <xsl:choose>
            <xsl:when test="string-length(@lemma) > 0">
                <xsl:value-of select="@lemma"/>
            </xsl:when>
            <xsl:otherwise><xsl:text>OUT</xsl:text></xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#x9;</xsl:text>
        <xsl:choose>
            <xsl:when test="string-length(@morph) > 0">
                <xsl:value-of select="@morph"/>
            </xsl:when>
            <xsl:otherwise><xsl:text>OUT</xsl:text></xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>
    <xsl:template match="@*">
        <xsl:copy/>
    </xsl:template>
</xsl:stylesheet>