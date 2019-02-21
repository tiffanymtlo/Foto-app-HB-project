$(function() {
  $('.tag').each((index, el) => {
    const $el = $(el);
    const top = parseFloat($el.data('top'));
    const left = parseFloat($el.data('left'));
    const width = parseFloat($el.data('width'));
    const height = parseFloat($el.data('height'));

    $el.css({
      width: width * 100 + '%',
      height: height * 100 + '%',
      top: top * 100 + '%',
      left: left * 100 + '%',
    });
  });
});
