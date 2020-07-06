// 消息提示框
function messagePop(value) {
    var str = '';
    str += '<div class="pop" style="display:none"><div class="pop-val">' + value + '</div></div>';

    $('body').append(str);
    $('.pop').fadeIn(200);

    $('.pop').css({
        'position': 'fixed',
        'width': '100%',
        'top': '0',
        'bottom': '0',
        'z-index': '1000'
    })
    $('.pop-val').css({
        'position': 'fixed',
        'width': '50%',
        'top': '40%',
        'background': 'rgba(0,0,0,.5)',
        'padding': '.2rem',
        'text-align': 'center',
        'left': '0',
        'right': '0',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'border-radius': '5px',
        'color': '#fff',
        'font-size': '100%'
    })

    setTimeout(closeDiv2, 2000);
    setTimeout(closeDiv3, 2300);

    function closeDiv2() {
        $('.pop').fadeOut(300);
    };

    function closeDiv3() {
        $('.pop').remove();
    };
}
