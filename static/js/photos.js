$(function() {
  $('.content__list-item').hover(function(){
    const $this = $(this);
    personId = $this.data('person-id');
    const $selectedDiv = $('[data-id="' + personId + '"]');
    $selectedDiv.css('opacity', 1);
    $this.addClass('content__list-item-hover');
  },
  function() {
    const $this = $(this);
    personId = $this.data('person-id');
    const $selectedDiv = $('[data-id="' + personId + '"]');
    $selectedDiv.css('opacity', 0);
    $this.removeClass('content__list-item-hover');
  });

  $('.tag').hover(function(){
    const $this = $(this);
    personId = $this.data('id');
    const $selectedItem = $('[data-person-id="' + personId + '"]');
    $selectedItem.addClass('content__list-item-hover');
  },
  function() {
    const $this = $(this);
    personId = $this.data('id');
    const $selectedItem = $('[data-person-id="' + personId + '"]');
    $selectedItem.removeClass('content__list-item-hover');
  });

  $('.photo-container').hover(function(){
    $('.tag').css('opacity', 1);
    $('.photo-wrapper').addClass('photo-wrapper-hover');
  },
  function() {
    $('.tag').css('opacity', 0);
    $('.photo-wrapper').removeClass('photo-wrapper-hover');
  });

  $('.photo__content__list').hover(function(){
    $('.photo-wrapper').addClass('photo-wrapper-hover');
  },
  function() {
    $('.photo-wrapper').removeClass('photo-wrapper-hover');
  });
});
