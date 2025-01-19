/* global requirejs */

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
    bootstrap: '/static/dashboard/js/vendor/bootstrap.bundle.min',
    jquery: '/static/dashboard/js/vendor/jquery-3.4.0.min',
    cookie: '/static/dashboard/js/vendor/js.cookie'
  }
})

requirejs(['cookie', 'bootstrap', 'jquery'], function (Cookies, bootstrap) {
  const csrftoken = Cookies.get('csrftoken')

  function csrfSafeMethod (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken)
      }
    }
  })

  const updateConfirmationDialog = function(title, message, action, onAction) {
    $('#confirmation_dialog h5.modal-title').html(title)
    $('#confirmation_dialog .modal-body').html(message)
    $('#confirmation_dialog button.btn-primary').html(action)

    $('#confirmation_dialog button.btn-primary').off('click')

    if (onAction !== undefined && onAction !== null) {
      $('#confirmation_dialog button.btn-primary').off('click')

      $('#confirmation_dialog button.btn-primary').on('click', onAction)
    }
  }

  const wireUpDelete = function() {
    $('.action-delete').off('click')

    $('.action-delete').click(function(eventObj) {
      eventObj.preventDefault()

      const listItem = $(this).parent()

      const elementType = $(this).attr('data-type')
      const elementValue = $(this).attr('data-value')

      const params = {
        'action': 'remove',
        'section': elementType,
        'value': elementValue
      }

      if (elementType === 'warning_sign') {
        updateConfirmationDialog('Remove warning sign?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'coping_skill') {
        updateConfirmationDialog('Remove coping skill?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'environmental_safety') {
        updateConfirmationDialog('Remove emvironmental safety?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'person_distraction') {
        updateConfirmationDialog('Remove person for distraction?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'person_help') {
        updateConfirmationDialog('Remove person for help?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'person_medical') {
        updateConfirmationDialog('Remove medical provider?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'person_mental') {
        updateConfirmationDialog('Remove mental health provider?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      } else if (elementType === 'person_mental') {
        updateConfirmationDialog('Remove mental health provider?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
          $.post(window.location.href, params, function(response, status, jqXHR) {
            listItem.remove()

            $('#confirmation_dialog').modal('hide')
          })
        })
      }

      $('#confirmation_dialog').modal('show')
    })

    $('.action-delete-reason').off('click')

    $('.action-delete-reason').click(function(eventObj) {
      eventObj.preventDefault()

      const listItem = $(this).parent()

      const elementId = $(this).attr('data-id')
      const elementValue = $(this).attr('data-value')

      const params = {
        'action': 'remove-reason',
        'section': 'reasons_for_living',
        'value': elementId
      }

      updateConfirmationDialog('Remove reason for living?', `Would you like to remove "${elementValue}" from your safety plan?`, 'Remove', function() {
        $.post(window.location.href, params, function(response, status, jqXHR) {
          listItem.remove()

          $('#confirmation_dialog').modal('hide')
        })
      })

      $('#confirmation_dialog').modal('show')
    })

    $('.reason-preview-image').off('click')

    $('.reason-preview-image').click(function(eventObj) {
      eventObj.preventDefault()

      $('#preview_image').attr('src', $(this).attr('data-image'))

      $('#preview_dialog').modal('show')
    })
  }

  $('.action-add').click(function(eventObj) {
    eventObj.preventDefault()

    const input = $(this).parent().find('input')

    const elementType = $(this).attr('data-type')
    const toAdd = input.val()

    const newElement = `<li class="list-group-item">${toAdd}<a href="#" class="action-delete" data-type="${elementType}" data-value="${toAdd}"><i class="bi bi-trash float-end"></i></a></li>`

    const addItem = $(this).parent().parent()

    const params = {
      'action': 'add',
      'section': elementType,
      'value': toAdd
    }

    $.post(window.location.href, params, function(response, status, jqXHR) {
      let newElement = `<li class="list-group-item">${toAdd}<a href="#" class="action-delete" data-type="${elementType}" data-value="${toAdd}"><i class="bi bi-trash float-end"></i></a></li>`

      if (elementType.startsWith('person_')) {
        newElement = `<li class="list-group-item"><i class="bi bi-chat-left message-tooltop" data-bs-toggle="tooltip" data-bs-title="(No message available.)"></i> ${toAdd}<a href="#" class="action-delete" data-type="${elementType}" data-value="${toAdd}"><i class="bi bi-trash float-end"></i></a></li>`
      }

      addItem.before(newElement)

      addItem.parent().find('.empty-list').hide()

      input.val('')

      wireUpDelete()
    })
  })

  $('.crisis_line_check').on('change', function(eventObj) {
    const checked = $(eventObj.target).prop('checked');
    const id = $(eventObj.target).attr('data-id')

    console.log(`CRISIS: ${id} = ${checked}`)

    const params = {
      'action': 'select-crisis-line',
      'section': 'crisis_text_lines',
      'line': `${id}`,
      'checked': `${checked}`
    }

    $.post(window.location.href, params, function(response, status, jqXHR) {

    })
  })

  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

  $('.message-tooltop').click(function(eventObj) {
    eventObj.preventDefault()

    let message = $(eventObj.target).attr('data-bs-title')

    if (message == '(No message available.)') {
      message = ''
    }

    const tooltip = $(this)

    $('#helper_message').val(message)

    const saveButton = $('#message_dialog .btn-primary')

    saveButton.off('click')

    const who = $(this).attr('data-value')
    const type = $(this).attr('data-type')

    saveButton.click(function(eventObj) {
      const newMessage = $('#helper_message').val()

      const params = {
        'action': 'update-message',
        'section': type,
        'person': who,
        'value': newMessage
      }

      $.post(window.location.href, params, function(response, status, jqXHR) {
        if (newMessage.trim() !== '') {
          tooltip.addClass('bi-chat-left-text-fill')
          tooltip.removeClass('bi-chat-left')
        } else {
          tooltip.removeClass('bi-chat-left-text-fill')
          tooltip.addClass('bi-chat-left')
        }

        $('#helper_message').val('')

        $('#message_dialog').modal('hide')
      })
    })

    $('#message_dialog').modal('show')
  })

  $('.input-group input.form-control').keypress(function(eventObj) {
    if (eventObj.which === 13) { // 13 is the key code for 'Enter'
      eventObj.preventDefault()

      $(this).parent().find('button').click()
    }
  })

  $('#button-reason').click(function(eventObj) {
    eventObj.preventDefault()

    const reasonField = $(this).parent().find('input.form-control')

    const reason = reasonField.val()

    var formData = new FormData();
    formData.append('action', 'add-reason')
    formData.append('section', 'reasons_for_living')
    formData.append('value', reason.trim())

    if ($('#reason_file').get(0).files.length > 0) {
      formData.append('reason_file', $('#reason_file')[0].files[0]);
    }

    const addItem = $(this).parent().parent()

    $.ajax({
      url: window.location.href,
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      success: function(response) {
        let newElement = '<li class="list-group-item">'

        if (response.image !== undefined) {
          newElement += `<a href="#" class="bi bi-image reason-preview-image" data-image="${response.image}"></a> `
        }

        newElement += `${reason} <a href="#" class="action-delete-reason float-end" data-type="reason_living" data-value="${reason.trim()}" data-id="${response.pk}"><i class="bi bi-trash float-end"></i></a></li>`

        addItem.before(newElement)

        reasonField.val('')

        $('#reason_file').val('')
        $('#button-reason-image').removeClass('btn-dark')
        $('#button-reason-image').addClass('btn-secondary')

        wireUpDelete()
      }
    })
  })

  $('#button-reason-image').click(function(eventObj) {
    eventObj.preventDefault()

    $('#reason_file').click()
  })

  $('#reason_file').on('change', function() {
    $('#button-reason-image').removeClass('btn-secondary')
    $('#button-reason-image').addClass('btn-dark')
  })

  wireUpDelete()
})
