# View
APP/output/views/view.py

## Purpose
Each View provides a form of output for the user of the testing framework to
see its output. Views can subscribe to signals from the model by providing
a dictionary mapping [Events](../events/event.md) to callbacks. (Return this
dictionary from `_get_event_subscriptions`).
