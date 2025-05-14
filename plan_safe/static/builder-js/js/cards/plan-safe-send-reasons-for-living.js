define(['material', 'cards/node', 'jquery'], function (mdc, Node) {
  class SendReasonsForLivingNode extends Node {
    editBody () {
      let body = ''

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `<div class="mdc-select mdc-select--outlined" id="${this.cardId}_select_mode" style="width: 100%">`
      body += '  <div class="mdc-select__anchor">'
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <span class="mdc-notched-outline__notch">'
      body += '        <span id="outlined-select-label" class="mdc-floating-label">Selection Mode</span>'
      body += '      </span>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += '    <span class="mdc-select__selected-text-container">'
      body += '      <span class="mdc-select__selected-text"></span>'
      body += '    </span>'
      body += '    <span class="mdc-select__dropdown-icon">'
      body += '      <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">'
      body += '        <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>'
      body += '        <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>'
      body += '      </svg>'
      body += '    </span>'
      body += '  </div>'
      body += '  <div class="mdc-select__menu mdc-menu mdc-menu-surface mdc-menu-surface--fullwidth">'
      body += `    <ul class="mdc-list" role="listbox" aria-label=Selected Element" id="${this.cardId}_element_list">`
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="sequential" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Sequential</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="random" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Random</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="random_no_repeat" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Random (No Repeats)</span>';
      body += '      </li>';
      body += '    </ul>'
      body += '  </div>'
      body += '</div>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_sample_count_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_sample_count_value" class="mdc-floating-label">Number to Send</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="number" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_sample_count_value" />`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_seconds_between_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_sample_count_value" class="mdc-floating-label">Delay Between Each (Seconds)</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="number" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_seconds_between_value" />`
      body += '  </label>'
      body += '</div>'


      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_message_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_variable_value" class="mdc-floating-label">Message</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `      <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="${this.cardId}_message_value"></textarea>`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7" style="padding-top: 16px;">'
      body += '  Next:'
      body += '</div>'
      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="padding-top: 8px; text-align: right;">'
      body += '  <button class="mdc-icon-button" id="' + this.cardId + '_next_edit">'
      body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>'
      body += '  </button>'
      body += '  <button class="mdc-icon-button" id="' + this.cardId + '_next_goto">'
      body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>'
      body += '  </button>'
      body += '</div>'

      body += '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">'
      body += '  <div class="mdc-dialog__container">'
      body += '    <div class="mdc-dialog__surface">'
      body += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>'
      body += '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content"  style="padding: 0px;">'

      body += this.dialog.chooseDestinationMenu(this.cardId)

      body += '      </div>'
      body += '    </div>'
      body += '  </div>'
      body += '  <div class="mdc-dialog__scrim"></div>'
      body += '</div>'

      return body
    }

    viewBody () {
      return `<div class="mdc-typography--body1" style="margin: 16px;">TODO Safety Plan (Fetch reason for living): <em>${this.definition}</em></div>`
    }

    initialize () {
      super.initialize()

      const me = this

      me.dialog.initializeDestinationMenu(me.cardId, function (selected) {
        me.definition.next_id = selected

        me.dialog.markChanged(me.id)
        me.dialog.loadNode(me.definition)
      })

      const dialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(me.cardId + '-edit-dialog'))

      $('#' + this.cardId + '_next_edit').on('click', function () {
        me.targetDestination = 'next'

        dialog.open()
      })

      $('#' + this.cardId + '_next_goto').on('click', function () {
        const destinationNodes = me.destinationNodes(me.dialog)

        for (let i = 0; i < destinationNodes.length; i++) {
          const destinationNode = destinationNodes[i]

          if (me.definition.next_id === destinationNode.id) {
            $("[data-node-id='" + destinationNode.id + "']").css('background-color', '#ffffff')
          } else {
            $("[data-node-id='" + destinationNode.id + "']").css('background-color', '#e0e0e0')
          }
        }

        const sourceNodes = me.sourceNodes(me.dialog)

        for (let i = 0; i < sourceNodes.length; i++) {
          const sourceNode = sourceNodes[i]

          if (me.definition.next_id === sourceNode.id) {
            $("[data-node-id='" + sourceNode.id + "']").css('background-color', '#ffffff')
          } else {
            $("[data-node-id='" + sourceNode.id + "']").css('background-color', '#e0e0e0')
          }
        }
      })

	  const messageField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_message_field`))

  	  if (this.definition.message_template !== undefined && this.definition.message_template !== null) {
	    messageField.value = this.definition.message_template
	  }

      $('#' + this.cardId + '_message_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_variable_value').val()

        me.definition.message_template = value
        
        console.log(me.definition)

        me.dialog.markChanged(me.id)
      })

	  const sampleCountField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_sample_count_field`))

  	  if (this.definition.count !== undefined && this.definition.count !== null) {
	    sampleCountField.value = "" + this.definition.count
	  }

      $('#' + this.cardId + '_sample_count_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_sample_count_value').val()

        me.definition.count = parseInt(value)

        console.log(me.definition)

        me.dialog.markChanged(me.id)
      })

	  const secondsBetweenField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_seconds_between_field`))

  	  if (this.definition.seconds_between !== undefined && this.definition.seconds_between !== null) {
	    secondsBetweenField.value = "" + this.definition.seconds_between
	  }

      $('#' + this.cardId + '_seconds_between_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_seconds_between_value').val()

        me.definition.seconds_between = parseInt(value)

        console.log(me.definition)

        me.dialog.markChanged(me.id)
      })

      const modeField = mdc.select.MDCSelect.attachTo(document.getElementById(`${me.cardId}_select_mode`))

  	  if (this.definition.mode !== undefined && this.definition.mode !== null) {
	    modeField.value = this.definition.mode
	  }

      modeField.listen('MDCSelect:change', () => {
        const originalMode = me.definition.mode
        
        me.definition.mode = modeField.value

        if (originalMode !== me.definition.mode) {
          me.dialog.markChanged(me.id)
        }
      })
    }

    destinationNodes (dialog) {
      const nodes = super.destinationNodes(dialog)

      const id = this.definition.next_id

      for (let i = 0; i < this.dialog.definition.length; i++) {
        const item = this.dialog.definition[i]

        if (item.id === id) {
          nodes.push(Node.createCard(item, dialog))
        }
      }

      if (nodes.length === 0) {
        const node = this.dialog.resolveNode(id)

        if (node !== null) {
          nodes.push(node)
        }
      }

      return nodes
    }

    updateReferences (oldId, newId) {
      if (this.definition.next_id === oldId) {
        this.definition.mext_id = newId
      }
    }

    cardType () {
      return 'Plan Safe: Send Reasons for Living'
    }

    static cardName () {
      return 'Plan Safe: Send Reasons for Living'
    }

    issues () {
      const issues = super.issues()
      
      if (this.definition.next_id === undefined) {
        issues.push([this.definition.id, 'Next node does not point to another node.', this.definition.name])
      } else if (this.definition.next_id === this.definition.id) {
        issues.push([this.definition.id, 'Next node points to self.', this.definition.name])
      } else if (this.isValidDestination(this.definition.next_id) === false) {
        issues.push([this.definition.id, 'Next node points to a non-existent node.', this.definition.name])
      }

      return issues
    }

    static createCard (cardName) {
      const card = {
        name: cardName,
        context: '(Context goes here...)',
        type: 'plan-safe-send-reasons-for-living',
        next_id: null,
        message_template: '#{{ reason.index }}: {{ reason.caption }}',
        seconds_between: 10,
        count: 1,
        mode: 'random_no_repeat',
        id: Node.uuidv4()
      }

      return card
    }
  }

  Node.registerCard('plan-safe-send-reasons-for-living', SendReasonsForLivingNode)

  return SendReasonsForLivingNode
})
