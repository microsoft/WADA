# {{topic_abbr}}

***{{catagory}}***



## Model Type

{{model}}

## Original Topic

{{topic}}

## Specified Topic

{{background}}

## Preference Summary

{{preference}}

## Debate History

{% for item in debate_history %}

***{{item.role_name}} :***

> {{item.content}}

{% endfor %}

## Result

{{judgement}}