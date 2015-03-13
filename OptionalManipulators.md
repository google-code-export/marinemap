# Implementation Details #

All the work is being done in the `feature_optional_manipulators` branch to keep default stable.

Quick brain dump of how this thing works:

  * manipulators field on MPA stores the current 'active' manipulator list
  * MPAs have an `active_manipulators` property which is the definitive list of manipulators to be applied (some extra logic and processing to the manipulators field).
  * manipulators field added to MPA forms as hidden field
  * rest app delivers modified json (distinguishes optional from required)
  * manipulators.js looks for the manipulators field and sets up a form. Hidden manipulators field used to determine initial state of checkboxes. Form is only visible when editing or creating shape.
  * manipulators.js is responsible for re-constructing the URL and populating the hidden manipulators field based on the form state.
  * MPA's apply\_manipulators now relies on MPA.active\_manipulators to get its manipulator list.


# Work that needs to be done on each MM instance #

  1. Add manipulators field to the MPA child class using south
```
  python manage.py schemamigration mlpa --auto
```
  1. MPAForm fields must include 'manipulators'
  1. Add optional manipulators to MPA model options
  1. Run install media (lots of js changes)

# RST Docs #

There may be cases where certain manipulators should be optional and user-selectable depending on the purpose of their MPA.
In this case we can specify `optional_manipulators` in the MPA model Options.

```
.. code-block:: python 

    class Options:
        manipulators = [ ClipToStudyRegionManipulator, ]
        optional_manipulators = [ EastWestManipulator, ]
```

On the user-interface side, when a user creates or edits a shape, there will be a form with checkboxes allowing them to select from these optional manipulators.

On the database side, the `active manipulators` that are applied to a given MPA are stored as a comma-separated string in the MPA table.
When and if the geometry needs to be saved again, the previously selected manipulators will be applied.
The required manipulators will always be applied regardless of the content of the MPA.manipulators field.
In other words, the MPA.manipulators field serves only to trigger the application of optional manipulators.

If there are no required manipulators, you must still provide an empty list for Options.manipulators

```
.. code-block:: python 

    class Options:
        manipulators = []
        optional_manipulators = [ ClipToStudyRegionManipulator, EastWestManipulator, ]
```

If the user doesn't select any other optional manipulators and there are none required, a special case is triggered. We can't allow any arbitrary input so the shape needs to be checked as a valid geometry at the very least. For this case, the `NullManipulator` is triggered which does nothing except ensure that the geometry is clean. Note that the NullManipulator should **not** appear in either your manipulators or optional\_manipulators lists.


When defining the manipulator itself, you can provide optional display\_name and description which will make for a more descriptive UI:

```
	    class Options:
	        name = 'YourManipulatorClass'
	        display_name = 'Your Manipulator Class'
	        description = 'Check it out. This is my brand new manipulator.'
```