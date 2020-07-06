(function () {
    function collection() {
        if (currentUserName) {
            var markObj = {};
            markObj.imgUrl = 'https://csdnimg.cn/release/phoenix/static_blog/images/appqr.png';
            var markPrompt = (new window.csdn.publicPrompt).init(markObj);
            var maeked = '您已经收藏过';
            if (!$(this).hasClass("liked")) {
                $.ajax({
                    url: 'https://my.csdn.net/my/favorite/do_add/2',
                    dataType: 'json',
                    type: 'POST',
                    xhrFields: {
                        withCredentials: true
                    },
                    data: {
                        title: articleTit,
                        url: curentUrl,
                        share: 1,
                        map_name: ''
                    },
                    success: function (data) {

                        if (data.succ == 1) {
                            $('.btn-bookmark').addClass("liked");
                            $('.article-footer-bookmark-btn').addClass("liked").children('span').text('已收藏');
                            markPrompt.show({})
                            // alert('收藏成功,可以在个人中心查看我的收藏');
                        } else {
                            if (data.msg === "您已经收藏过") {
                                $('.btn-bookmark').addClass("liked");
                                $('.article-footer-bookmark-btn').addClass("liked").children('span').text('已收藏');
                                markPrompt.show({
                                    titleStr: maeked
                                })
                            } else {
                                alert(data.msg);

                            }
                        }
                    }
                });
            } else {
                markPrompt.show({
                    titleStr: maeked
                })
            }
        } else {
            window.csdn.loginBox.show();
        }
    }

    window.csdn = window.csdn ? window.csdn : {};
    window.csdn.articleCollection = collection;

    function setArticleH(btnReadmore, posi) {
        var winH = $(window).height();
        var articleBox = $("div.article_content");
        var artH = articleBox.height();
        if (artH > winH * posi) {
            articleBox.css({
                'height': winH * posi + 'px',
                'overflow': 'hidden'
            });
            btnReadmore.click(function () {
                articleBox.removeAttr("style");
                $(this).parent().remove()
            })
        } else {
            btnReadmore.parent().remove()
        }
    }

    var btnReadmore = $("#btn-readmore");
    $('.article-footer-bookmark-btn').click(window.csdn.articleCollection)
    if (btnReadmore.length > 0) {
        if (currentUserName) {
            setArticleH(btnReadmore, 3);
        } else {
            setArticleH(btnReadmore, 1.2);
        }
    } else {
        $('.hide-article-box').addClass('hide-article-style');
    }
})();