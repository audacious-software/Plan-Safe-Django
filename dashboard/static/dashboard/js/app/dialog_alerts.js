/* global requirejs, $ */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    bootstrap: {
      deps: ['jquery']
    },
    cookie: {
      exports: 'Cookies'
    }
  },
  baseUrl: '/static/dashboard/js/app',
  paths: {
    app: '/static/dashboard/js/app',
    material: '/static/dashboard/js/vendor/material-components-web-11.0.0',
    jquery: '/static/dashboard/js/vendor/jquery-3.4.0.min',
    cookie: '/static/dashboard/js/vendor/js.cookie',
    moment: '/static/dashboard/js/vendor/moment-with-locales'
  }
})

requirejs(['material', 'jquery', 'base'], function (mdc) {
  const select = mdc.select.MDCSelect.attachTo(document.querySelector('.mdc-select'))

  const url = URL.parse(window.location.href)

  if (url.searchParams.get('limit') !== null) {
    select.value = url.searchParams.get('limit')
  } else {
    select.value = '25'
  }

  select.listen('MDCSelect:change', () => {
    const url = URL.parse(window.location.href)
    url.searchParams.set('limit', select.value)
    window.location.href = url.href
  })

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('alerts_table'))

  $('.mdc-data-table__pagination-button').click(function (eventObj) {
    eventObj.preventDefault()

    const url = $(this).attr('data-url')

    window.location.href = url
  })
})
