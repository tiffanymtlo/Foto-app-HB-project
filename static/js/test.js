$(function() {
  $('.tag').each((idx, el) => {
    const $el = $(el);
    const top = $el.data('top');
    const left = $el.data('left');
    const width = $el.data('width');
    const height = $el.data('height');


    $el.css({
      width,
      height,
      top,
      left,
    });
  });
  // $('.tag').hide();
  // $(".photo").mouseenter(function () {
  //       $('.tag').show();
  //   });
  //   $(".photo").mouseleave(function () {
  //       $('.tag').hide();
  //   });

});
