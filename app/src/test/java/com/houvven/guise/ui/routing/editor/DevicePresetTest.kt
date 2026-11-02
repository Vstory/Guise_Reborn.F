package com.houvven.guise.ui.routing.editor

import com.houvven.guise.device.DeviceBrand
import com.houvven.guise.device.DeviceModel
import com.houvven.guise.xposed.config.ModuleConfig
import com.houvven.guise.xposed.config.ModuleConfigState
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class DevicePresetTest {

    private val brand = DeviceBrand(
        key = "xiaomi",
        displayName = "小米",
        buildBrand = "Xiaomi",
        manufacturer = "Xiaomi",
        models = listOf(
            DeviceModel(model = "23127PN0CC", name = "Xiaomi 14", device = "houji", alias = "houji", type = "mob"),
            DeviceModel(model = "M2011J18C", name = "MIX FOLD", device = "J18", alias = "cetus", type = "mob"),
        ),
    )

    @Test
    fun randomModelPullsModelDeviceAndFingerprintTogether() {
        val state = ModuleConfigState.of(ModuleConfig(brand = "Xiaomi", androidVersion = "15"))
        val models = brand.models.map { it.model }.toSet()
        val devices = brand.models.map { it.resolvedDevice() }.toSet()

        repeat(50) {
            applyDevicePreset(state, randomDevicePreset(state, brand))

            assertTrue("型号不在该品牌型号池里：${state.model.value}", state.model.value in models)
            assertTrue("设备代号不在该品牌型号池里：${state.device.value}", state.device.value in devices)
            // 指纹必须跟着新型号走，否则 Build.MODEL 与 Build.FINGERPRINT 自相矛盾
            assertTrue(
                "指纹没跟上型号：${state.fingerPrint.value}",
                state.fingerPrint.value.startsWith("Xiaomi/${state.device.value}/${state.device.value}:15/"),
            )
            assertTrue("指纹里没有本次 Build ID", state.fingerPrint.value.contains(state.buildId.value))
            assertTrue(state.fingerPrint.value.endsWith(":user/release-keys"))
        }
    }

    @Test
    fun randomModelKeepsConfiguredProductInsteadOfInventingOne() {
        val state = ModuleConfigState.of(ModuleConfig(brand = "Xiaomi", androidVersion = "15", product = "custom"))
        applyDevicePreset(state, randomDevicePreset(state, brand))

        assertEquals("custom", state.product.value)
        assertTrue(state.fingerPrint.value.startsWith("Xiaomi/custom/${state.device.value}:15/"))
    }

    @Test
    fun unknownBrandLeavesIdentityUntouched() {
        val state = ModuleConfigState.of(
            ModuleConfig(model = "A1", device = "d1", fingerPrint = "keep", buildId = "BID"),
        )

        assertEquals("A1:d1", randomDevicePreset(state, null))
        assertEquals("keep", state.fingerPrint.value)
        assertEquals("BID", state.buildId.value)
    }
}
