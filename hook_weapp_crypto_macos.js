    // filename: hook_weapp_crypto_macos.js

    // 等待进程附加成功
    // 注意: 在 macOS 上 Hook JS 环境可能需要一些技巧来定位正确的上下文
    // 这可能不是直接访问全局变量那么简单
    // 您可能需要 Hook JS 引擎创建或执行脚本的时机

    console.log("Frida script loaded.");

    // !!! 这个示例是高度概念性的，您需要找到小程序 JS 运行的实际上下文 !!!
    // 可能需要更复杂的探索，例如 Hook 微信内部负责加载或运行小程序 JS 的原生方法
    // 或者 Hook 相关的 WebView 方法

    // 假设 userCryptoManager 存在于某个全局对象下 (例如 window 或一个特定的 Worker 上下文)
    // 真实的路径可能复杂得多
    const targetObject = globalThis; // 尝试全局对象，或者需要找到小程序运行的具体 JS 上下文

    // 检查 targetObject 是否存在 userCryptoManager 属性
    if (typeof targetObject.userCryptoManager !== 'undefined') {
        console.log("Found userCryptoManager object.");

        // 检查 getLatestUserKey 方法是否存在
        if (typeof targetObject.userCryptoManager.getLatestUserKey === 'function') {
            console.log("Found getLatestUserManager.getLatestUserKey method.");

            // Hook the method
            Interceptor.attach(targetObject.userCryptoManager.getLatestUserKey.implementation, {
                onEnter: function(args) {
                    console.log("Entering userCryptoManager.getLatestUserKey");
                    // 参数通常从 args[2] 开始，但取决于具体的调用约定
                    // 对于纯 JS 方法，参数可能直接在 arguments 伪数组中
                    console.log("  Arguments:", JSON.stringify(Array.from(arguments))); // 打印参数
                },
                onLeave: function(retval) {
                     console.log("Leaving userCryptoManager.getLatestUserKey");
                     // retval 是方法的返回值
                     // 如果返回值是对象，可能需要进一步处理才能打印详细内容
                     console.log("  Return Value:", JSON.stringify(retval)); // 打印返回值
                }
            });

            console.log("Successfully hooked userCryptoManager.getLatestUserKey.");

        } else {
            console.error("userCryptoManager.getLatestUserKey is not a function or not found on the object.");
        }
    } else {
        console.error("userCryptoManager object not found in the target context.");
    }

    // 如果小程序运行在原生层桥接的 JSContext 中 (iOS) 或 V8 引擎中 (Android/其他)，
    // Hook 方式会涉及 Hook 原生代码层的方法，这些方法负责将 userCryptoManager 暴露给 JS。
    // 例如，在 iOS 上可能需要 Hook 涉及到 JSContext evaluation 或对象注入的方法。
    
