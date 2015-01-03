import collections

def parse_resource_list(data, is_output=False):
    resources = {}

    data = iter(data)
    while True:
        name = next(data, None)
        if name is None:
            return resources

        value = next(data)
        
        if is_output:
            unknown = next(data)

        resources[name] = value

def extract_converters(part):
    for module in part.get('MODULE', []):
        if 'ConverterName' in module:
            name = module['ConverterName']
            inputs = {}
            if 'RecipeInputs' in module:
                inputs = parse_resource_list(module['RecipeInputs'], False)
            outputs = {}
            if 'RecipeOutputs' in module:
                outputs = parse_resource_list(module['RecipeOutputs'], True)            
            yield name, inputs, outputs

def extract_all_converters(parts):
    converters = collections.defaultdict(dict)
    
    for part_name, part in parts.items():
        for converter_name, inputs, outputs in extract_converters(part):
            converters[part_name][converter_name] = {
                "part_name": part_name,
                "converter_name": converter_name,
                "inputs": inputs,
                "outputs": outputs
            }

    return converters
    
def extract_names(items):
    for item in items:
        yield item['name'], item
        
def filter_parts_only(items):
    for key, item in items.items():
        if 'PART' in item:
            yield item['PART']

def filter_mks_parts(items):
    for name, item in items:
        if name.startswith('MKS_'):
            yield name, item

def load_mks_parts(raw_data):
    parts = filter_parts_only(raw_data)
    named_parts = extract_names(parts)
    mks_parts = dict(filter_mks_parts(named_parts))

    return mks_parts

def build_resource_lists(converters, include_converter_name=False, ignore=set()):        
    sources = collections.defaultdict(set)
    depends = collections.defaultdict(set)

    for part_name, part_converters in converters.items():
        for converter_name, converter in part_converters.items():
            
            name = part_name
            if include_converter_name:
                name += converter_name

            for resource_name in converter['inputs'].keys():
                if resource_name in ignore:
                    continue
                depends[resource_name].add(name)
                
            for resource_name in converter['outputs'].keys():
                if resource_name in ignore:
                    continue
                sources[resource_name].add(name)

    return sources, depends
