
import difflib

WEATHER={"sunny":"clear","bright":"clear","cloudy":"soft_overcast","overcast":"soft_overcast","grey":"soft_overcast","gray":"soft_overcast","drizzle":"light_rain","rain":"light_rain","rainy":"light_rain","storm":"storm","stormy":"storm","thunderstorm":"storm","snow":"snow","snowy":"snow","blizzard":"snow","fog":"mist","foggy":"mist","misty":"mist"}
LABEL={"clear":"Clear","soft_overcast":"Soft overcast","light_rain":"Light rain","heavy_rain":"Heavy rain","mist":"Mist","snow":"Snow","storm":"Storm"}
LOCS=("bus_stop","village_road","bakery","village_green","ashcroft_cottage")

def closest(v,valid,default):
    v=str(v or "").strip().lower().replace(" ","_")
    if v in valid:return v
    m=difflib.get_close_matches(v,list(valid),n=1,cutoff=.25)
    return m[0] if m else default

def location(v,current):
    t=str(v or "").lower()
    aliases={"outside":"village_green","green":"village_green","park":"village_green","shop":"bakery","bread":"bakery","home":"ashcroft_cottage","cottage":"ashcroft_cottage","road":"village_road","bus":"bus_stop"}
    for k,x in aliases.items():
        if k in t:return x
    return closest(t,LOCS,current)

def weather(raw,s):
    raw=raw if isinstance(raw,dict) else {"state":raw}
    cur=s["weather"]; v=str(raw.get("state") or raw.get("weather") or raw.get("label") or "").lower()
    v=WEATHER.get(v,v.replace(" ","_")); v=closest(v,LABEL,cur["state"])
    if v==cur["state"]:
        cycle=["clear","soft_overcast","mist","light_rain","heavy_rain","storm","snow"]
        v=cycle[(cycle.index(v)+1)%len(cycle)]
    try: temp=max(-10,min(35,int(raw.get("temperature_c",cur["temperature_c"]))))
    except: temp=cur["temperature_c"]
    return {"state":v,"label":str(raw.get("label") or LABEL[v])[:40],"temperature_c":temp,"wind":str(raw.get("wind") or cur.get("wind","light"))[:40]}

def npc(raw,s):
    raw=raw if isinstance(raw,dict) else {}; items=raw.get("changes") if isinstance(raw.get("changes"),list) else []
    ids=list(s["npcs"]); out=[]
    for x in items[:4]:
        if not isinstance(x,dict):continue
        i=closest(x.get("npc") or x.get("name"),ids,ids[0]); cur=s["npcs"][i]["location"]
        act=str(x.get("activity") or x.get("intent") or "taking a short break")[:160]
        dest=location(x.get("destination") or act,cur)
        if dest==cur: dest=next((q for q in LOCS if q!=cur),cur)
        out.append({"npc":i,"activity":act,"destination":dest})
    if not out:
        i=ids[s["village_brain"]["pulse_count"]%len(ids)]; cur=s["npcs"][i]["location"]
        out=[{"npc":i,"activity":"taking a brief walk and seeing who is about","destination":"village_green" if cur!="village_green" else "village_road"}]
    return {"changes":out}

def traffic(raw,s):
    raw=raw if isinstance(raw,dict) else {}; items=raw.get("changes") if isinstance(raw.get("changes"),list) else []
    ids=list(s["traffic"]); out=[]
    for x in items[:3]:
        if not isinstance(x,dict):continue
        i=closest(x.get("vehicle") or x.get("name"),ids,ids[0]); cur=s["traffic"][i]["location"]
        act=str(x.get("activity") or x.get("intent") or "continuing its route")[:160]
        dest=location(x.get("destination") or act,cur)
        if dest==cur:dest="village_road" if cur!="village_road" else "village_green"
        out.append({"vehicle":i,"activity":act,"destination":dest})
    if not out:
        i=ids[s["village_brain"]["pulse_count"]%len(ids)]; cur=s["traffic"][i]["location"]
        out=[{"vehicle":i,"activity":"moving through Bellwether on its ordinary route","destination":"village_road" if cur!="village_road" else "village_green"}]
    return {"changes":out}

def conversation(raw,s):
    raw=raw if isinstance(raw,dict) else {}; items=raw.get("interactions") if isinstance(raw.get("interactions"),list) else []
    ids=list(s["npcs"]); out=[]
    for x in items[:3]:
        if not isinstance(x,dict):continue
        ps=x.get("participants") or []; ps=ps if isinstance(ps,list) else [ps]
        mapped=[]
        for p in ps:
            i=closest(p,ids,ids[0])
            if i not in mapped:mapped.append(i)
        if len(mapped)<2:mapped.append(next(i for i in ids if i not in mapped))
        s["npcs"][mapped[1]]["location"]=s["npcs"][mapped[0]]["location"]
        topic=str(x.get("topic") or "the changing weather")[:100]
        out.append({"participants":mapped[:2],"topic":topic,"summary":str(x.get("summary") or f"They exchange a few words about {topic}.")[:220]})
    if not out:
        a,b=ids[:2]; s["npcs"][b]["location"]=s["npcs"][a]["location"]
        out=[{"participants":[a,b],"topic":"the day's small changes","summary":"Two villagers pause to exchange news before returning to their routines."}]
    return {"interactions":out}

def repair_world_round(raw,s):
    raw=raw if isinstance(raw,dict) else {}
    return {"weather":weather(raw.get("weather",{}),s),"npc":npc(raw.get("npc",{}),s),"traffic":traffic(raw.get("traffic",{}),s),"conversation":conversation(raw.get("conversation",{}),s)}
