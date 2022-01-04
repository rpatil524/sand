import { RStore, SingleKeyIndex, SingleKeyUniqueIndex } from "rma-baseapp";
import { SERVER } from "../../env";

export interface Property {
  id: string;
  uri: string;
  label: string;
  readableLabel: string;
  aliases: string[];
  description: string;
  parents: string[];
}

export class PropertyStore extends RStore<string, Property> {
  constructor() {
    super(
      `${SERVER}/api/properties`,
      { readableLabel: "readable_label" },
      false,
      [new SingleKeyUniqueIndex("uri")]
    );
  }

  get uriIndex() {
    return this.indices[0] as SingleKeyUniqueIndex<string, string, Property>;
  }

  getPropertyByURI = (uri: string): Property | undefined => {
    const id = this.uriIndex.index.get(uri);
    return id !== undefined ? this.get(id)! : undefined;
  };
}
