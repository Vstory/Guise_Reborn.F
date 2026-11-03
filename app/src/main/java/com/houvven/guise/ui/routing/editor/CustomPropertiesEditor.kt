package com.houvven.guise.ui.routing.editor

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.houvven.guise.R
import com.houvven.guise.xposed.config.CustomProperty
import com.houvven.guise.xposed.config.ModuleConfigState
import com.houvven.guise.xposed.config.isBuiltinPropertyKey
import com.houvven.guise.xposed.config.isValidPropertyKey

/**
 * 自定义系统属性的编辑区：补足内置字段覆盖不到的 OS 特有属性（如 MIUI 版本号）。
 *
 * 行直接落在 state 上（不在本地留副本），清空配置时能与其它字段一起被清掉。
 */
@Composable
internal fun CustomPropertiesEditor(state: ModuleConfigState) {
    val rows = state.customProperties.value

    fun writeBack(updated: List<CustomProperty>) {
        state.customProperties.value = updated
    }

    Title(
        text = stringResource(R.string.title_custom_properties),
        supportingText = stringResource(R.string.custom_property_summary),
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 15.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        rows.forEachIndexed { index, property ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                OutlinedTextField(
                    value = property.key,
                    onValueChange = { updated ->
                        writeBack(rows.toMutableList().also { it[index] = property.copy(key = updated) })
                    },
                    label = { Text(stringResource(R.string.custom_property_key)) },
                    singleLine = true,
                    isError = property.key.isNotBlank() &&
                        (isBuiltinPropertyKey(property.key) || !isValidPropertyKey(property.key.trim())),
                    supportingText = if (property.key.isNotBlank() && isBuiltinPropertyKey(property.key)) {
                        { Text(stringResource(R.string.custom_property_key_conflict)) }
                    } else if (property.key.isNotBlank() && !isValidPropertyKey(property.key.trim())) {
                        { Text(stringResource(R.string.custom_property_key_invalid)) }
                    } else {
                        null
                    },
                    modifier = Modifier.weight(1f),
                )
                OutlinedTextField(
                    value = property.value,
                    onValueChange = { updated ->
                        writeBack(rows.toMutableList().also { it[index] = property.copy(value = updated) })
                    },
                    label = { Text(stringResource(R.string.custom_property_value)) },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                IconButton(
                    onClick = { writeBack(rows.toMutableList().also { it.removeAt(index) }) },
                ) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = stringResource(R.string.custom_property_remove),
                    )
                }
            }
        }

        TextButton(onClick = { writeBack(rows + CustomProperty()) }) {
            Text(stringResource(R.string.custom_property_add))
        }
    }
}
