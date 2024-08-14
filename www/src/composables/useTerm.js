import {onMounted, ref, watch} from 'vue'
import {FitAddon} from 'xterm-addon-fit'
import {Terminal} from 'xterm'

/**
 * @name: useTerm，用于统一使用terminal
 * @description: 终端
 * @return {Promise}
 *
 * 示例用法：
 * 创建终端
 * <div ref="terminalRef" style="width: 100%;height: 100%"/>
 * const {term, terminalRef, initTerm} = useTerm()
 * 手动初始化
 * await initTerm()
 * 写入内容
 * term.value.write('写入terminal 内容\n')
 */
export default function useTerm() {
  const term = ref(null)
  const terminalRef = ref(null)
  const fitAddon = new FitAddon()

  function initTerm() {
    return new Promise((resolve) => {
      setTimeout(() => {
          console.log('init terminal')
          term.value = new Terminal({
            rendererType: 'canvas',
            disableStdin: false,
            convertEol: true,
            cursorStyle: 'block',
            scrollback: 9999999,
          })
          term.value.open(terminalRef.value)
          term.value.loadAddon(fitAddon)
          fitAddon.fit()
          term.value.focus()
          resolve()
        }, 300
      )
    })
  }

  window.onresize = function () {
    fitAddon.fit()
  }


  return {
    term,
    terminalRef,
    initTerm
  }
}