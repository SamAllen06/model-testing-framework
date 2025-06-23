# Views 
APP/src/output/views/

## Purpose
Views are modules that subscribe to [events](../events/events.md) and produce
output that can be used by the user later.

## Functionality
This module provides a ViewType enum which allows a controller to enable the
views it wants using [view_manager.](../view_manager.md)

Each view class must be a subclass of [View](view.md). They can map
[Event(s)](../events/event.md) to callback functions by implementing
`_get_event_subscriptions`. Views do not have to subscribe to all events, nor do
they have to accept all keyword arguments that an event provides to its
callbacks.

This implementation is used as part of the implementation for [View's](view.md)
method `subscribe_to_bus`, which is called by [view_manager](../view_manager.md)
to subscribe a view's callbacks to each event when it is enabled.
