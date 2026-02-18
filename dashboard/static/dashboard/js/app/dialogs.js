/* global requirejs, alert, $ */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    cookie: {
      exports: 'Cookies'
    },
    bootstrap: {
      deps: ['jquery']
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

requirejs(['material', 'cookie', 'moment', 'jquery', 'base'], function (mdc, Cookies, moment) {
  // console.log(mdc);

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('dialogs_table'))

  const addDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add_dialog_dialog'))

  const deleteDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('confirm_delete_dialog'))

  const lockDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('lock_delete_dialog'))

  const addDialogName = mdc.textField.MDCTextField.attachTo(document.getElementById('new_dialog_name'))

  $('#fab_add_dialog').click(function (eventObj) {
    addDialogName.value = ''

    $('#new_dialog_clone_id').val('')

    addDialog.open()
  })

  $('.dialog_clone_button').click(function (eventObj) {
    addDialogName.value = $(eventObj.target).data().cloneName

    $('#new_dialog_clone_id').val($(eventObj.target).data().cloneId)

    addDialog.open()
  })

  $('.dialog_delete_button').click(function (eventObj) {
    $('#delete_dialog_name').text($(eventObj.target).data().deleteName)
    $('#delete_dialog_id').val($(eventObj.target).data().deleteId)

    deleteDialog.open()
  })

  $('.dialog_lock_button').click(function (eventObj) {
    lockDialog.open()
  })

  deleteDialog.listen('MDCDialog:closed', function (event) {
    const action = event.detail.action

    if (action === 'close') {
      // Do nothing
    } else if (action === 'delete') {
      const deleteId = $('#delete_dialog_id').val()

      $.post('/dashboard/delete', {
        identifier: deleteId
      }, function (data) {
        window.location.reload()
      })
    }
  })

  addDialog.listen('MDCDialog:closed', function (event) {
    const action = event.detail.action

    if (action === 'close') {
      // Do nothing
    } else if (action === 'create') {
      const cloneId = $('#new_dialog_clone_id').val()

      $.post('/dashboard/create', {
        name: addDialogName.value,
        identifier: cloneId
      }, function (data) {
        window.location.reload()
      })
    }
  })

  const scheduleDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('schedule_dialog'))

  const dateField = mdc.textField.MDCTextField.attachTo(document.getElementById('start_date'))
  const phoneField = mdc.textField.MDCTextField.attachTo(document.getElementById('dialog_phone_number'))
  const internalMinutesField = mdc.textField.MDCTextField.attachTo(document.getElementById('dialog_spacing_internal_minutes'))
  const interruptMinutesField = mdc.textField.MDCTextField.attachTo(document.getElementById('dialog_interrupt_minutes'))
  const timeoutsField = mdc.textField.MDCTextField.attachTo(document.getElementById('dialog_spacing_internal_timeouts'))
  const dialogVariablesField = mdc.textField.MDCTextField.attachTo(document.getElementById('dialog_variables'))

  scheduleDialog.listen('MDCDialog:closed', function (event) {
    const action = event.detail.action

    if (action === 'close') {
    // Do nothing - just close
    } else if (action === 'schedule') {
      const identifier = $('#schedule_identifier').val()

      const payload = {
        identifier,
        date: dateField.value,
        interrupt_minutes: interruptMinutesField.value,
        pause_minutes: internalMinutesField.value,
        timeout_minutes: timeoutsField.value,
        dialog_variables: dialogVariablesField.value,
        phone: phoneField.value
      }

      $.post('/dashboard/schedule', payload, function (data) {
        if (data.message !== undefined) {
          alert(data.message)
        }
      })
    }
  })

  $('.dialog_start_button').click(function (eventObj) {
    const identifier = $(this).attr('data-start-id')

    dateField.value = moment().format('YYYY-MM-DDTHH:mm')
    interruptMinutesField.value = ''
    internalMinutesField.value = ''
    timeoutsField.value = ''
    phoneField.value = ''

    $('#schedule_identifier').val(identifier)

    scheduleDialog.open()
  })

  const pageSizeSelect = mdc.select.MDCSelect.attachTo(document.querySelector('.mdc-data-table__pagination-rows-per-page-select--outlined'))

  pageSizeSelect.listen('MDCSelect:change', () => {
    const searchParams = new URLSearchParams(window.location.search)

    searchParams.set('size', pageSizeSelect.value)
    searchParams.delete('page')

    window.location = 'dialogs?' + searchParams.toString()
  })
})
