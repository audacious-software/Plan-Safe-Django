define(['material', 'cards/node', 'jquery'], function (mdc, Node) {
  class FetchReasonsForLivingNode extends Node {
    editBody () {
      let body = ''

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-4">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_sample_count_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_sample_count_value" class="mdc-floating-label">Sample Count</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="number" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_sample_count_value" />`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-8 mdc-form-field">'
      body += '  <div class="mdc-checkbox">'
      body += `    <input type="checkbox" class="mdc-checkbox__native-control" id="${this.cardId}_avoid_repeats" />`
      body += '    <div class="mdc-checkbox__background">'
      body += '      <svg class="mdc-checkbox__checkmark" viewBox="0 0 24 24">'
      body += '        <path class="mdc-checkbox__checkmark-path" fill="none" d="M1.73,12.91 8.1,19.28 22.79,4.59"/>'
      body += '      </svg>'
      body += '      <div class="mdc-checkbox__mixedmark"></div>'
      body += '    </div>'
      body += '    <div class="mdc-checkbox__ripple"></div>'
      body += '    <div class="mdc-checkbox__focus-ring"></div>'
      body += '  </div>'
      body += `  <label for="${this.cardId}_avoid_repeats">Avoid Repeats</label>`
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      body += `  <label class="mdc-text-field mdc-text-field--outlined mdc-text-field--textarea" id="${this.cardId}_variable_field" style="width: 100%">`
      body += '    <span class="mdc-notched-outline">'
      body += '      <span class="mdc-notched-outline__leading"></span>'
      body += '      <div class="mdc-notched-outline__notch">'
      body += `        <label for="${this.cardId}_variable_value" class="mdc-floating-label">Variable Name</label>`
      body += '      </div>'
      body += '      <span class="mdc-notched-outline__trailing"></span>'
      body += '    </span>'
      body += `    <input type="text" class="mdc-text-field__input" style="width: 100%" id="${this.cardId}_variable_value" />`
      body += '  </label>'
      body += '</div>'

      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7" style="padding-top: 16px;">'
      body += '  No reasons available:'
      body += '</div>'
      body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="padding-top: 8px; text-align: right;">'
      body += '  <button class="mdc-icon-button" id="' + this.cardId + '_empty_edit">'
      body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>'
      body += '  </button>'
      body += '  <button class="mdc-icon-button" id="' + this.cardId + '_empty_goto">'
      body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>'
      body += '  </button>'
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
        if (me.targetDestination === 'next') {
	        me.definition.next_id = selected
	    } else if (me.targetDestination === 'empty') {
	        me.definition.empty_id = selected
	    }

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

      $('#' + this.cardId + '_empty_edit').on('click', function () {
        me.targetDestination = 'empty'

        dialog.open()
      })

      $('#' + this.cardId + '_empty_goto').on('click', function () {
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

	  const variableField = mdc.textField.MDCTextField.attachTo(document.getElementById(`${this.cardId}_variable_field`))

  	  if (this.definition.variable !== undefined && this.definition.variable !== null) {
	    variableField.value = this.definition.variable
	  }

      $('#' + this.cardId + '_variable_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_variable_value').val()

        me.definition.variable = value
        
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

      const avoidRepeats = $(`#${this.cardId}_avoid_repeats`)

  	  if (this.definition.avoid_repeats !== undefined && this.definition.avoid_repeats !== null) {
	  	avoidRepeats.prop('checked', this.definition.avoid_repeats)
	  }

      $('#' + this.cardId + '_avoid_repeats').on('change', function () {
        me.definition.avoid_repeats = avoidRepeats.prop('checked')

        console.log(me.definition)

        me.dialog.markChanged(me.id)
      })
    }

    destinationNodes (dialog) {
      const nodes = super.destinationNodes(dialog)

      let id = this.definition.empty_id

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

      id = this.definition.next_id

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

      if (this.definition.empty_id === oldId) {
        this.definition.empty_id = newId
      }
    }

    cardType () {
      return 'Plan Safe: Fetch Reasons for Living'
    }

    static cardName () {
      return 'Plan Safe:Fetch Reasons for Living'
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

      if (this.definition.empty_id === undefined) {
        issues.push([this.definition.id, 'Empty node does not point to another node.', this.definition.name])
      } else if (this.definition.empty_id === this.definition.id) {
        issues.push([this.definition.id, 'Empty node points to self.', this.definition.name])
      } else if (this.isValidDestination(this.definition.empty_id) === false) {
        issues.push([this.definition.id, 'Empty node points to a non-existent node.', this.definition.name])
      }

      if (this.definition.variable === undefined) {
        issues.push([this.definition.id, 'Variable not defined.', this.definition.name])
      }

      return issues
    }

    static createCard (cardName) {
      const card = {
        name: cardName,
        context: '(Context goes here...)',
        type: 'plan-safe-fetch-reasons-for-living',
        next_id: null,
        empty_id: null,
        variable: null,
        count: 1,
        avoid_repeats: true,
        id: Node.uuidv4()
      }

      return card
    }
  }

  Node.registerCard('plan-safe-fetch-reasons-for-living', FetchReasonsForLivingNode)

  return FetchReasonsForLivingNode
})
