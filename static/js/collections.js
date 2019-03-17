$(function() {
  $('.grid').masonry({
    itemSelector: '.grid-item',
    columnWidth: 330,
    gutter: 10
  });

  $('.more-persons__show-more').on('click', function() {
    $('.collection__content__persons-list').css('height', '110px');
    $('.person-item-row').css('height', '50%');
    $('.more-persons-caption-container').css('display', 'none');
  });

  $('.persons__show-less').on('click', function() {
    $('.collection__content__persons-list').css('height', '55px');
    $('.person-item-row').css('height', '100%');
    $('.more-persons-caption-container').css('display', 'block');
  });
});
