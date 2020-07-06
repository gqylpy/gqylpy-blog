$(document).click(function () {
    $('.nav-list').removeClass('open')
});
$('.nav-menu,.nav-list').click(function (e) {
    e.stopPropagation()
});
$('nav').find('.nav-menu').click(function (e) {
    $('.nav-list').toggleClass('open')
})