# pylint: disable=no-member, line-too-long

import datetime

from .models import Participant, StudyArm, TimeZone

def process_records(records): # pylint: disable=too-many-locals, too-many-branches
    # Don't enroll unless admin_arm_1.trt is non-empty: "1" = control, "2" = intervention

    # Wire up REDCap (trt is the randomization variable)
    # REDCAP ID: record_id [NOTE: Located in event enrollment_arm_1]
    # Phone number: phone_number [NOTE: Located in event enrollment_arm_1]
    # Personalized Name: first_name or if name_preferred is present, use that.  [NOTE: Located in event enrollment_arm_1]
    # Time zone: time_zone [NOTE: Located in event enrollment_arm_1]
    #       1 = Hawaiian-Aleutian Time
    #       2 = Alaskan Time
    #       3 = Pacific Time
    #       4 = Mountain Time
    #       5 = Central Time
    #       6 = Eastern Time
    # Day Start: time_early [NOTE: Located in event enrollment_arm_1]
    # Day End: time_late [NOTE: Located in event enrollment_arm_1]
    # Study Arm: trt [NOTE: Located in event admin_arm_1]

    merged = {}

    for record in records:
        identifier = record.get('%s.record_id' % record.get('redcap_event', ''), None)

        if identifier is not None:
            existing = merged.get(identifier, None)

            if existing is None:
                existing = {}

                merged[identifier] = existing

            for key in record.keys():
                value = record.get(key, '')

                if value != '':
                    existing[key] = value

    for identifier in merged:
        record = merged.get(identifier)

        condition = record.get('admin_arm_1.trt', None)

        if condition is not None:
            enrolled = Participant.objects.filter(metadata__redcap_id=identifier).first()

            if enrolled is not None:
                print('ALREADY ENROLLED: %s - %s - %s' % (identifier, condition, enrolled.pk))

                # print(json.dumps(record, indent=2))
            else:
                print('CREATE RECORD FOR: %s - %s' % (identifier, condition))

                local_id = Participant.objects.generate_identifier(prefix='RCT-', digits=8)

                metadata = {
                    'redcap_id': identifier
                }

                phone_number = record.get('enrollment_arm_1.phone_number', None)

                preferred_name = record.get('enrollment_arm_1.name_preferred', None)

                if preferred_name is None:
                    preferred_name = record.get('enrollment_arm_1.first_name', None)

                selected_zone = None

                time_zone = record.get('enrollment_arm_1.time_zone', None)

                if time_zone == '1':
                    selected_zone = TimeZone.objects.get(name='Pacific/Honolulu')
                elif time_zone == '2':
                    selected_zone = TimeZone.objects.get(name='America/Anchorage')
                elif time_zone == '3':
                    selected_zone = TimeZone.objects.get(name='America/Los_Angeles')
                elif time_zone == '4':
                    selected_zone = TimeZone.objects.get(name='America/Denver')
                elif time_zone == '5':
                    selected_zone = TimeZone.objects.get(name='America/Chicago')
                elif time_zone == '6':
                    selected_zone = TimeZone.objects.get(name='America/New_York')

                start_time = datetime.datetime.strptime(record.get('enrollment_arm_1.time_early', None), '%H:%M').time()

                end_time = datetime.datetime.strptime(record.get('enrollment_arm_1.time_late', None), '%H:%M').time()

                arm = None

                study_arm = record.get('admin_arm_1.trt', None)

                if study_arm == '1':
                    arm = StudyArm.objects.get(identifier='control')
                elif study_arm == '2':
                    arm = StudyArm.objects.get(identifier='experiment')

                Participant.objects.create_participant(phone_number, preferred_name, selected_zone.name, arm.identifier, start_time, end_time, identifier=local_id, metadata=metadata)
