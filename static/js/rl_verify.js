var flag = true;  // {# 用于滑块校验 #}
var reg_username = false;
var login_username = false;
var $reg_username = $("#reg_username");
var $csrfmiddlewaretoken = $("[name='csrfmiddlewaretoken']").val();
var $reg_username_err = $("#reg_username_err");
var $reg_password = $("#reg_password");
var $reg_password_err = $("#reg_password_err");
var $reg_re_password = $("#reg_re_password");
var $reg_re_password_err = $("#reg_re_password_err");
var $login_username = $("#login_username");
var $login_username_err = $("#login_username_err");
var $login_password = $("#login_password");
var $login_password_err = $("#login_password_err");
var $login_err = $("#login_err");


(function () {
    // 隐藏顶部的搜索按钮
    $('#search-box').css('display', 'none');
})();


// ----------------------注册校验相关----------------------

// {# 验证用户名是否已存在 #}
$($reg_username).on("input", function () {
    $.ajax({
        url: "/auth/is_user_exists",
        type: "POST",
        data: {
            username: $($reg_username).val(),
            csrfmiddlewaretoken: $csrfmiddlewaretoken,
        },
        success: function (data) {
            if (data) {
                $($reg_username_err).text("用户名已被使用");
            } else {
                $($reg_username_err).text('');
                reg_username = true;
            }
        }
    })
});

// {# 验证密码格式 #}
$reg_password.blur(function () {
    if ($reg_password.val() && $reg_password.val().length < 6) {
        console.log(123);
        $reg_password_err.text('密码至少6位');
        $reg_re_password_err.text('');
        return;
    }
    if ($reg_password.val() && $reg_re_password.val() && $reg_password.val() !== $reg_re_password.val()) {
        $reg_re_password_err.text('密码不一致');
    }
    if (!$reg_password.val()) {
    $reg_re_password_err.text('');
    }
});
$reg_password.click(function () {
    $reg_password_err.text('');
    $reg_re_password_err.text('');
});

// {# 验证确认密码格式 #}
$reg_re_password.blur(function () {
    if ($reg_password.val().length >= 6 && $reg_re_password.val() && $reg_password.val() !== $reg_re_password.val()) {
        $reg_re_password_err.text('密码不一致');
    } else {
        $reg_re_password_err.text('');
    }
});
$reg_re_password.click(function () {
    $reg_re_password_err.text('');
});

// {# 注册按钮 #}
function reg_sub() {
    // {# 加密密码  #}
    var pTag = document.getElementById('reg_password');
    if (pTag.value) {  // 如果用户输入了密码
        pTag.value = hex_md5(pTag.value);
        var rpTag = document.getElementById('reg_re_password');
        rpTag.value = hex_md5(rpTag.value);
    }
}


// // ----------------------登录校验相关----------------------

// {# 验证用户是否存在 #}
$($login_username).blur(function () {
    if ($login_username.val()) {
        $.ajax({
            url: "/auth/is_user_exists",
            type: "POST",
            data: {
                username: $($login_username).val(),
                csrfmiddlewaretoken: $csrfmiddlewaretoken,
            },
            success: function (data) {
                if (data) {
                    $($login_username_err).text('');
                    login_username = true;
                } else {
                    $($login_username_err).text("用户不存在");
                }
            }
        })
    }
});

$($login_username.click(function () {
    $($login_username_err).text('');
    $login_err.text('');
}));
$login_password.click(function () {
    $($login_password_err).text('');
    $login_err.text('');
});

// {# 登录按钮 #}
function log_sub() {
    if (!flag) {
        document.getElementById('msg').innerHTML = '<span style="color: red;">向右滑动滑块来校验！</span>'
    } else {
        if ($login_password.val()) {
            // {# 加密密码  #}
            var pTag = document.getElementById('login_password');
            pTag.value = hex_md5(pTag.value);
        }
    }
}


// {# 滑块验证 #}
// jigsaw.init(document.getElementById('captcha'), function () {
//     flag = true;
//     document.getElementById('login_btn').setAttribute('type', 'submit');
//     document.getElementById('msg').innerHTML = '<span style="color: green;">校验通过！</span>';
// });