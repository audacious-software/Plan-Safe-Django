define(['material', 'cards/node', 'jquery'], function (mdc, Node) {
  class UpdateSafetyPlanNode extends Node {
    editBody () {
      let body = ''

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `<div class="mdc-select mdc-select--outlined" id="${this.cardId}_select_element" style="width: 100%">`
      body += '  <div class="mdc-select__anchor">'
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <span class="mdc-notched-outline__notch">'
      body += '        <span id="outlined-select-label" class="mdc-floating-label">Selected Element</span>'
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
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="warning-signs" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Warning Signs</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="coping-skills" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Coping Skills</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="people-distraction" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">People For Distraction</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="people-help" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">People For Help</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="crisis-helplines" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Crisis Help Lines</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="provider-medical" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Medical Provider</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="provider-mental-health" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Mental Health Provider</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="environmental-safety" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Environmental Safety</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="reasons-for-living" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Reasons For Living</span>';
      body += '      </li>';
      body += '    </ul>'
      body += '  </div>'
      body += '</div>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `<div class="mdc-select mdc-select--outlined" id="${this.cardId}_select_operation" style="width: 100%">`
      body += '  <div class="mdc-select__anchor">'
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <span class="mdc-notched-outline__notch">'
      body += '        <span id="outlined-select-label" class="mdc-floating-label">Operation</span>'
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
      body += `    <ul class="mdc-list" role="listbox" aria-label=Selected Element" id="${this.cardId}_operation_list">`
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="operation-add" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Add To&#8230;</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="operation-remove" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Remove From&#8230;</span>';
      body += '      </li>';
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="operation-reset" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Reset</span>';
      body += '      </li>';
      body += '    </ul>'
      body += '  </div>'
      body += '</div>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_contact_name_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_message_value" class="mdc-floating-label">Contact Name</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="text" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_contact_name_value" />`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_phone_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_message_value" class="mdc-floating-label">Phone Number</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="text" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_phone_value" />`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_message_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_message_value" class="mdc-floating-label">Message</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += '    <span class="mdc-text-field__resizer">'
      body += `      <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="${this.cardId}_message_value"></textarea>`
      body += '    </span>'
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_value_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_message_value" class="mdc-floating-label">Value</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += '    <span class="mdc-text-field__resizer">'
      body += `      <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="${this.cardId}_value_value"></textarea>`
      body += '    </span>'
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `<div class="mdc-select mdc-select--outlined" id="${this.cardId}_select_image" style="width: 100%">`
      body += '  <div class="mdc-select__anchor">'
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <span class="mdc-notched-outline__notch">'
      body += '        <span id="outlined-select-label" class="mdc-floating-label">Image</span>'
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
      body += `    <ul class="mdc-list" role="listbox" aria-label=Selected Element" id="${this.cardId}_image_list">`
      body += '      <li class="mdc-list-item" aria-selected="false" data-value="operation-add" role="option">';
      body += '        <span class="mdc-list-item__ripple"></span>';
      body += '        <span class="mdc-list-item__text">Last Sent&#8230;</span>';
      body += '      </li>';
      body += '    </ul>'
      body += '  </div>'
      body += '</div>'
      body += '</div>'


      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">'
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
      return `<div class="mdc-typography--body1" style="margin: 16px;">TODO Safety Plan: <em>${this.definition}</em></div>`
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

  	  const contactNameField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_contact_name_field`))
  	  
  	  if (this.definition.contact_name !== undefined && this.definition.contact_name !== null) {
	    contactNameField.value = this.definition.contact_name
	  }

	  const phoneField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_phone_field`))

  	  if (this.definition.phone !== undefined && this.definition.phone !== null) {
	    phoneField.value = this.definition.phone
	  }

	  const valueField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_value_field`))

  	  if (this.definition.value !== undefined && this.definition.value !== null) {
	    valueField.value = this.definition.value
	  }

	  const messageField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_message_field`))

  	  if (this.definition.message !== undefined && this.definition.message !== null) {
	    messageField.value = this.definition.message
	  }

      const imageField = mdc.select.MDCSelect.attachTo(document.getElementById(`${me.cardId}_select_image`))

      imageField.listen('MDCSelect:change', () => {
        const originalImage = me.definition.image
        me.definition.image = imageField.value

        if (originalImage !== me.definition.image) {
          me.dialog.markChanged(me.id)
        }
      })
      
      const updateFieldVisibility = function() {
	   	console.log(`updateFieldVisibility`)
	   	console.log(me.definition)
    
      	if (me.definition.field == null || me.definition.operation == null || me.definition.operation == 'operation-reset') {
	      	$(`#${me.cardId}_contact_name_field`).hide()
	      	$(`#${me.cardId}_phone_field`).hide()
	      	$(`#${me.cardId}_value_field`).hide()
	      	$(`#${me.cardId}_message_field`).hide()
	      	$(`#${me.cardId}_select_image`).hide()
      	} else if (me.definition.operation == 'operation-add') {
      		const peopleFields = [
      			'people-distraction',
      			'people-help',
      			'provider-medical',
      			'provider-mental-health'
      		]

      		const textFields = [
      			'warning-signs',
      			'coping-skills',
      			'crisis-helplines',
      			'environmental-safety'
      		]

	    	console.log(`Field: ${me.definition.field}`)
      		
      		if (peopleFields.includes(me.definition.field)) {
		    	console.log(`People field: ${me.definition.field}`)
		      	$(`#${me.cardId}_contact_name_field`).show()
		      	$(`#${me.cardId}_phone_field`).show()
		      	
		      	$(`#${me.cardId}_value_field`).hide()
		      	$(`#${me.cardId}_message_field`).hide()
		      	$(`#${me.cardId}_select_image`).hide()
		    } else if (textFields.includes(me.definition.field)) {
		    	console.log(`Text field: ${me.definition.field}`)

		      	$(`#${me.cardId}_message_field`).show()

		      	$(`#${me.cardId}_contact_name_field`).hide()
		      	$(`#${me.cardId}_phone_field`).hide()
		      	$(`#${me.cardId}_value_field`).hide()
		      	$(`#${me.cardId}_select_image`).hide()
		    } else if (me.definition.field == 'reasons-for-living') {
		      	$(`#${me.cardId}_message_field`).show()
		      	$(`#${me.cardId}_select_image`).show()

		      	$(`#${me.cardId}_contact_name_field`).hide()
		      	$(`#${me.cardId}_phone_field`).hide()
		      	$(`#${me.cardId}_value_field`).hide()
		    } else {
		    	console.log(`Unknown field: ${me.definition.field}`)
		      	$(`#${me.cardId}_contact_name_field`).hide()
		      	$(`#${me.cardId}_phone_field`).hide()
	    	  	$(`#${me.cardId}_value_field`).hide()
	      		$(`#${me.cardId}_message_field`).hide()
		      	$(`#${me.cardId}_select_image`).hide()
		    }
      	}
      }

      const selectField = mdc.select.MDCSelect.attachTo(document.getElementById(`${me.cardId}_select_element`))

      selectField.listen('MDCSelect:change', () => {
        const originalField = me.definition.field
        me.definition.field = selectField.value

        if (originalField !== me.definition.field) {
          me.dialog.markChanged(me.id)
        }
        
        updateFieldVisibility()
      })

      const operationField = mdc.select.MDCSelect.attachTo(document.getElementById(`${me.cardId}_select_operation`))

      operationField.listen('MDCSelect:change', () => {
        const originalOperation = me.definition.operation
        me.definition.operation = operationField.value

        if (originalOperation !== me.definition.operation) {
          me.dialog.markChanged(me.id)
        }

        updateFieldVisibility()
      })
      
      updateFieldVisibility()
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
        this.definition.next_id = newId
      }
    }

    cardType () {
      return 'Plan Safe: Update Safety Plan'
    }

    static cardName () {
      return 'Plan Safe: Update Safety Plan'
    }

    issues () {
      const issues = super.issues()
      
      /*

      if (this.definition.next_id === undefined) {
        issues.push([this.definition.id, 'Next node does not point to another node.', this.definition.name])
      } else if (this.definition.next_id === this.definition.id) {
        issues.push([this.definition.id, 'Next node points to self.', this.definition.name])
      } else if (this.isValidDestination(this.definition.next_id) === false) {
        issues.push([this.definition.id, 'Next node points to a non-existent node.', this.definition.name])
      }

      if (this.definition.error_id === undefined) {
        issues.push([this.definition.id, 'Error node does not point to another node.', this.definition.name])
      } else if (this.definition.error_id === this.definition.id) {
        issues.push([this.definition.id, 'Error node points to self.', this.definition.name])
      } else if (this.isValidDestination(this.definition.error_id) === false) {
        issues.push([this.definition.id, 'Error node points to a non-existent node.', this.definition.name])
      }

      if (this.definition.key === undefined || this.definition.key === undefined) {
        issues.push([this.definition.id, 'Variable key not defined.', this.definition.name])
      }
      */

      return issues
    }

    static createCard (cardName) {
      const card = {
        name: cardName,
        context: '(Context goes here...)',
        type: 'plan-safe-update-safety-plan',
        next_id: null,
        field: null,
        value: null,
        operation: null,
        id: Node.uuidv4()
      }

      return card
    }
  }

  Node.registerCard('plan-safe-update-safety-plan', UpdateSafetyPlanNode)

  return UpdateSafetyPlanNode
})
