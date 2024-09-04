/* global requirejs, FormData, alert, confirm */

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
    moment: '/static/dashboard/js/vendor/moment-with-locales',
    jquery: '/static/dashboard/js/vendor/jquery-3.4.0.min',
    cookie: '/static/dashboard/js/vendor/js.cookie'
  }
})

requirejs(['material', 'cookie', 'moment', 'jquery', 'base'], function (mdc, Cookies, moment) {
  const dataTable = mdc.dataTable.MDCDataTable.attachTo(document.getElementById('participants_data_table'))
  const pageSizeSelect = mdc.select.MDCSelect.attachTo(document.querySelector('.mdc-data-table__pagination-rows-per-page-select--outlined'))

  pageSizeSelect.listen('MDCSelect:change', () => {
    const searchParams = new URLSearchParams(window.location.search)

    searchParams.set('size', pageSizeSelect.value)
    searchParams.delete('page')

    window.location = 'participants?' + searchParams.toString()
  })

  mdc.textField.MDCTextField.attachTo(document.getElementById('search_field'))

  $('#search_field input').on('keypress', function (event) {
    if (event.originalEvent.keyCode === 13) {
      const searchParams = new URLSearchParams(window.location.search)

      searchParams.set('query', event.target.value)
      searchParams.delete('study_arm')
      searchParams.delete('language')

      window.location = 'participants?' + searchParams.toString()
    }
  })

  const broadcastMessageField = mdc.textField.MDCTextField.attachTo(document.getElementById('broadcast_message_field'))
  const broadcastWhenMessageField = mdc.textField.MDCTextField.attachTo(document.getElementById('broadcast_when_field'))

  const confirmBroadcastDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('confirm_broadcast'))

  $('#broadcast_message_field textarea').keyup(function (event) {
    if (broadcastMessageField.value.length > 0) {
      $('#button_broadcast_click').removeAttr('disabled')
    } else {
      $('#button_broadcast_click').attr('disabled', 'true')
    }
  })

  $('#button_broadcast_click').attr('disabled', 'true')

  $('#button_broadcast_click').click(function (eventObj) {
    const selectedIds = dataTable.getSelectedRowIds()

    const identifiers = []

    $.each(selectedIds, function (index, value) {
      identifiers.push(value.replace('participant_row_', ''))
    })

    const attachment = $('#attachment')[0].files[0]

    const formData = new FormData()

    formData.append('identifiers', JSON.stringify(identifiers))
    formData.append('message', broadcastMessageField.value)
    formData.append('when', broadcastWhenMessageField.value)
    formData.append('attachment', attachment)

    const dateString = broadcastWhenMessageField.value.replace('T', ' ')

    let when = moment()

    if (dateString !== '') {
      when = moment(dateString)
    }

    const now = moment()

    if (when <= now) {
      $('#warning-in-past').show()
    } else {
      $('#warning-in-past').hide()
    }

    if (when.hour() < 8 || when.hour() > 17) {
      $('#warning-outside-workday').show()
    } else {
      $('#warning-outside-workday').hide()
    }

    $('#confirm-broadcast-count').html('' + identifiers.length)

    $('#confirm-broadcast-when').html(when.format('LLLL'))

    if (when < now) {
      $('#confirm-broadcast-when').css('color', '#800000')
    } else {
      $('#confirm-broadcast-when').removeAttr('style')
    }

    $('#confirm-broadcast-message').html(broadcastMessageField.value)

    const confirmListener = function (event) {
      const action = event.detail.action

      confirmBroadcastDialog.unlisten('MDCDialog:closed', confirmListener)

      if (action === 'close') {
        // Do nothing - just close
      } else if (action === 'schedule') {
        $.ajax({
          url: '/dashboard/participants/broadcast',
          type: 'POST',
          success: function (data) {
            if (data.message !== undefined) {
              window.alert(data.message)
            }

            if (data.reset) {
              broadcastMessageField.value = ''
              $('#button_broadcast_click').attr('disabled', 'true')
              $('#button_attach_click i').html('attach_file')
              $('#label_attach_click').html('<i>No file selected</i>')
              $('#attachment').val('')
            }

            if (data.reload) {
              window.location.reload()
            }
          },
          data: formData,
          cache: false,
          processData: false,
          contentType: false,
          enctype: 'multipart/form-data'
        })
      }
    }

    confirmBroadcastDialog.listen('MDCDialog:closed', confirmListener)

    confirmBroadcastDialog.open()
  })

  $('#button_attach_click').click(function (eventObj) {
    $('#attachment').click()
  })

  $('#attachment').on('change', function (e) {
    console.log(this.files)

    if (this.files[0].size > 5 * 1024 * 1024) {
      alert('Cannot send a file larger than 5 MB. Please select another.')
      $(this).val('')
    } else {
      $('#button_broadcast_click').removeAttr('disabled')
      $('#button_attach_click i').html('file_download_done')
      $('#label_attach_click').html(this.files[0].name)
    }
  })

  const addParticipantDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add_participant_dialog'))

  const addParticipantIdentifier = mdc.textField.MDCTextField.attachTo(document.getElementById('new_participant_id'))
  const addParticipantPhone = mdc.textField.MDCTextField.attachTo(document.getElementById('new_participant_phone'))
  const addParticipantPersonalizedName = mdc.textField.MDCTextField.attachTo(document.getElementById('new_participant_personalized_name'))

  $('#fab_add_participant').click(function (eventObj) {
    addParticipantIdentifier.value = ''
    addParticipantPhone.value = ''
    addParticipantPersonalizedName.value = ''

    $('input[name="new_participant_timezone"]:checked').attr('checked', false)
    $('input[name="new_participant_study_arm"]:checked').attr('checked', false)

    addParticipantDialog.open()
  })

  addParticipantDialog.listen('MDCDialog:closed', function (event) {
    const action = event.detail.action

    if (action === 'close') {
      // Do nothing - just close
    } else if (action === 'create') {
      const payload = {
        identifier: addParticipantIdentifier.value,
        phone_number: addParticipantPhone.value,
        personalized_name: addParticipantPersonalizedName.value,
        study_arm: $('input[name="new_participant_study_arm"]:checked').val(),
        time_zone: $('input[name="new_participant_time_zone"]:checked').val()
      }

      $.post('/dashboard/participants', payload, function (data) {
        if (data.message !== undefined) {
          window.alert(data.message)
        }

        if (data.reload) {
          window.location.reload()
        }
      })
    }
  })

  $('.message_user').click(function (eventObj) {
    window.location = $(this).attr('data-link')
  })

  const updateParticipantDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('update_participant_dialog'))

  const updateParticipantIdentifier = mdc.textField.MDCTextField.attachTo(document.getElementById('update_participant_id'))
  const updateParticipantPhone = mdc.textField.MDCTextField.attachTo(document.getElementById('update_participant_phone'))
  const updateParticipantPersonalizedName = mdc.textField.MDCTextField.attachTo(document.getElementById('update_participant_personalized_name'))

  $('.update_user').click(function (eventObj) {
    updateParticipantIdentifier.value = $(this).attr('data-user-id')
    updateParticipantPhone.value = $(this).attr('data-phone')
    updateParticipantPersonalizedName.value = $(this).attr('data-personalized-name')

    $('input[name="update_participant_timezone"]:checked').attr('checked', false)
    $('input[name="update_participant_study_arm"]:checked').attr('checked', false)

    $('input[name="update_participant_timezone"][value="' + $(this).attr('data-time-zone') + '"]').attr('checked', true)
    $('input[name="update_participant_study_arm"][value="' + $(this).attr('data-study-arm') + '"]').attr('checked', true)

    updateParticipantDialog.open()
  })

  updateParticipantDialog.listen('MDCDialog:closed', function (event) {
    const action = event.detail.action

    if (action === 'close') {
      // Do nothing - just close
    } else if (action === 'update') {
      const payload = {
        identifier: updateParticipantIdentifier.value,
        phone_number: updateParticipantPhone.value,
        personalized_name: updateParticipantPersonalizedName.value,
        time_zone: $('input[name="update_participant_timezone"]:checked').val(),
        study_arm: $('input[name="update_participant_study_arm"]:checked').val()
      }

      $.post('/dashboard/participants', payload, function (data) {
        if (data.message !== undefined) {
          window.alert(data.message)
        }

        if (data.reload) {
          window.location.reload()
        }
      })
    }
  })
})
