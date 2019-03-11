$(function() {
  $('.upload__form').on('submit', function() {
    const $uploadContainer = $('.upload__container');
    const $uploadLoader = $('.upload__loader');
    $uploadContainer.removeClass('show').addClass('hide');
    $uploadLoader.removeClass('hide').addClass('show');
  });
});
