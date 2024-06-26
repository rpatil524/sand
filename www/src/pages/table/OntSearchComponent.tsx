import { WithStyles, withStyles } from "@material-ui/styles";
import { Select, Spin } from "antd";
import { observer } from "mobx-react";
import { useEffect, useState } from "react";
import { useStores } from "../../models";
import SearchOptionsComponent from "./SearchOptionsComponent";
import { debounce } from "lodash";
import { SearchOptions } from "./NodeSearchComponent";
import { ClassTextSearchResult } from "../../models/ontology/ClassStore";
import { PropertyTextSearchResult } from "../../models/ontology/PropertyStore";
import { EntityTextSearchResult } from "../../models/entity/EntityStore";

const styles = {
  selection: {
    width: "100%",
  },
};

type SearchProps = {
  defaultSearchQuery?: string;
  value?: string | string[];
  onDeselect?: (value: string) => void;
  onSelect?: (value: string) => void;
  mode?: "multiple" | "tags";
} & WithStyles<typeof styles>;

export const OntPropSearchComponent = withStyles(styles)(
  observer((props: SearchProps) => {
    return useSearchComponent("propertyStore", props);
  })
);

export const OntClassSearchComponent = withStyles(styles)(
  observer((props: SearchProps) => {
    return useSearchComponent("classStore", props);
  })
);

export const EntitySearchComponent = withStyles(styles)(
  observer((props: SearchProps) => {
    return useSearchComponent("entityStore", props);
  })
);

function useSearchComponent(
  storeName: "propertyStore" | "classStore" | "entityStore",
  props: SearchProps
) {
  const store = useStores()[storeName];
  const [searchOptions, setSearchOptions] = useState<SearchOptions[]>();

  // search for additional values if it's not in the list
  const onSearch = (query: string) => {
    if (query === "") {
      return;
    }

    const loaderOption: SearchOptions = {
      id: "",
      label: <Spin style={{ width: "100%", marginTop: 3 }} size="large" />,
      value: "",
    };

    setSearchOptions([loaderOption]);
    store.findByName(query).then((data) => {
      let searchResults: SearchOptions[] = data.map(
        (
          searchResult:
            | ClassTextSearchResult
            | PropertyTextSearchResult
            | EntityTextSearchResult
        ) => {
          return {
            id: searchResult.id,
            label: (
              <SearchOptionsComponent
                id={searchResult.id}
                description={searchResult.description}
                label={searchResult.label}
              />
            ),
            value: searchResult.id,
          };
        }
      );
      setSearchOptions(searchResults);
    });
  };

  // if default search query is provided, we should do an initial search to get the results so users
  // can click immediately -- this is a work around to antd lack of setting a default query.
  // however, the dropdown isn't triggered by default -- we can improve it so it save users one click
  useEffect(() => {
    if (props.defaultSearchQuery !== undefined) {
      onSearch(props.defaultSearchQuery);
    }
  }, [props.defaultSearchQuery || ""]);

  return (
    <Select
      allowClear={true}
      options={searchOptions}
      onClear={() => setSearchOptions([])}
      defaultActiveFirstOption={false}
      className={props.classes.selection}
      showSearch={true}
      onSearch={debounce(onSearch, 300)}
      value={props.value === undefined ? undefined : props.value}
      filterOption={false}
      onSelect={
        props.onSelect === undefined
          ? undefined
          : (value: any, option: SearchOptions) => {
              store.fetchById(option.id).then(() => {
                props.onSelect!(option.id);
              });
            }
      }
      onDeselect={props.onDeselect as any}
    />
  );
}
