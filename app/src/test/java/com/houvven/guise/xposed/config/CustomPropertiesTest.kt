package com.houvven.guise.xposed.config

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CustomPropertiesTest {
    @Test
    fun acceptsDottedPropertyKeys() {
        assertTrue(isValidPropertyKey("ro.miui.ui.version.name"))
        assertTrue(isValidPropertyKey("persist.sys.timezone"))
        assertTrue(isValidPropertyKey("ro.build.version.sdk"))
    }

    @Test
    fun rejectsMalformedKeys() {
        assertFalse(isValidPropertyKey(""))
        assertFalse(isValidPropertyKey("ro.miui version"))
        assertFalse(isValidPropertyKey("ro.miui-version"))
        assertFalse(isValidPropertyKey("ro.小米"))
    }

    @Test
    fun recognizesBuiltinKeysAfterTrimming() {
        assertTrue(isBuiltinPropertyKey(" ro.product.model "))
        assertFalse(isBuiltinPropertyKey("ro.miui.ui.version.name"))
    }

    @Test
    fun sanitizeDropsBuiltinBlankAndEmptyValueEntries() {
        val sanitized = sanitizeCustomProperties(
            listOf(
                CustomProperty("ro.miui.ui.version.name", "14"),
                CustomProperty("  ro.miui.ui.version.code  ", "13"),
                CustomProperty("ro.product.model", "TA-1000"),
                CustomProperty("", "orphan"),
                CustomProperty("ro.empty.value", ""),
                CustomProperty("ro.bad key", "x"),
            )
        )

        assertEquals(
            mapOf(
                "ro.miui.ui.version.name" to "14",
                "ro.miui.ui.version.code" to "13",
            ),
            sanitized,
        )
    }

    @Test
    fun sanitizeKeepsPartiallyFilledRowsOutOfConfig() {
        assertEquals(emptyMap<String, String>(), sanitizeCustomProperties(emptyList()))
        assertEquals(
            emptyMap<String, String>(),
            sanitizeCustomProperties(listOf(CustomProperty(), CustomProperty(key = "ro.a"))),
        )
    }
}
