package ai.hicoffer.agent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/** HiCoffer Android 개발 환경 뼈대 — 화면 1개. 삭제 기능 없음(격리·이동·되돌리기만, 설계안 S-08). */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Column(Modifier.padding(24.dp)) {
                    Text("Hi Coffer")
                    Text("Android 개발 환경 0.0.1 · Hi DAM 자체 표준")
                }
            }
        }
    }
}
