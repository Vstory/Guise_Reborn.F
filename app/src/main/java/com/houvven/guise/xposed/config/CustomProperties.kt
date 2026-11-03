package com.houvven.guise.xposed.config

import kotlinx.serialization.Serializable

/**
 * 自定义系统属性的一行。
 *
 * 存 List 而不是 Map：编辑过程中键会短暂为空或重复，Map 承载不了这个中间态；
 * 收敛成可用的键值对是 hook 侧的职责（[sanitizeCustomProperties]）。
 */
@Serializable
data class CustomProperty(
    var key: String = "",
    var value: String = "",
)

/**
 * 与内置字段同源的属性键。
 *
 * 这些键由 `OsBuildHook` 统一维护（同时改 Build.XXX 静态字段），自定义再写一遍会让
 * Build.MODEL 与 getprop 说法不一致 —— 比「改不了」更容易被检测出来。
 */
internal val BUILTIN_PROPERTY_KEYS: Set<String> = setOf(
    "ro.product.brand",
    "ro.product.manufacturer",
    "ro.product.model",
    "ro.product.name",
    "ro.product.device",
    "ro.product.board",
    "ro.hardware",
    "ro.build.id",
    "ro.build.fingerprint",
    "ro.build.version.release",
    "ro.build.version.sdk",
)

internal fun isValidPropertyKey(key: String): Boolean =
    key.isNotEmpty() && key.all { it in 'a'..'z' || it in 'A'..'Z' || it in '0'..'9' || it == '.' || it == '_' }

internal fun isBuiltinPropertyKey(key: String): Boolean = key.trim() in BUILTIN_PROPERTY_KEYS

/** 收敛成可直接注入的属性表：丢掉空键、空值与内置键，键去首尾空白。 */
internal fun sanitizeCustomProperties(raw: List<CustomProperty>): Map<String, String> =
    raw.mapNotNull { property ->
        val key = property.key.trim()
        when {
            !isValidPropertyKey(key) -> null
            property.value.isEmpty() -> null
            key in BUILTIN_PROPERTY_KEYS -> null
            else -> key to property.value
        }
    }.toMap()
