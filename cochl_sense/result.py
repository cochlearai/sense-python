import json

class Event:
    def __init__(self, json):
        self.tag = json["tag"]
        self.probability = json["probability"]
        self.start_time = json["start_time"]
        self.end_time = json["end_time"]

    def __repr__(self):
        return str(vars(self))

class EventEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Event):
            return {
                "tag": o.tag,
                "probability": o.probability,
                "start_time": o.start_time,
                "end_time": o.end_time,
            }
        return json.JSONEncoder.default(self, o)

def default_event_filter(event):
    return True

class Result:
    def __init__(self, raw):        
        raw_json = json.loads(raw)
        result = raw_json["result"]
        self.__service = result["task"]
        self.__events = [Event(json_frame) for json_frame in result["frames"]]
        self.use_default_filter()

    def __str__(self):
        return str(self.__events)

    def set_filter(self, filter):
        self.__filter = filter

    def use_default_filter(self):
        self.__filter = default_event_filter

    def service(self):
        return self.__service
    
    def all_events(self):
        return self.__events

    def to_json(self):
        return json.dumps({
            "events": self.all_events(),
            "service": self.service()
        }, cls=EventEncoder)

    def detected_events(self):
        return [event for event in self.all_events() if self.__filter(event)]

    def detected_tags(self):
        tags = [frame.tag for frame in self.detected_events()]
        return sorted(set(tags))

    def detected_events_timing(self):
        summary = {}
        for event in self.detected_events():
            timings = summary.get(event.tag, [])
            timings.append((event.start_time, event.end_time))
            summary[event.tag] = timings
        
        for tag in summary:
            summary[tag] = _merge_overlapping_events(summary[tag])

        return summary

    def _append_new_result(self, raw, max_events_history_size):
        raw_json = json.loads(raw)
        result = raw_json["result"]
        new_events = [Event(json_frame) for json_frame in result["frames"]]
        self.__events = self.__events[len(self.__events) - max_events_history_size:] + new_events

def _merge_overlapping_events(times):
    if len(times) == 0:
        return []

    times = sorted(times)

    merged = [times[0]]
    
    for time in times[1:]:
        last = merged[-1]
        if time[0] > last[1]:
            merged.append(time)
            continue
        if time[1] > last[1]:
            merged[-1] = (last[0], time[1])

    return merged