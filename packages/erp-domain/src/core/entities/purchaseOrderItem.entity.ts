export class PurchaseOrderItem {
  public readonly id: string;
  public readonly poId: string;
  public readonly articleId: string;
  public readonly qty: number;
  public readonly uom: string;
  public readonly price: number;
  public readonly taxKeyId?: string;
  public readonly deliveryDate?: Date;

  constructor(data: {
    id: string;
    poId: string;
    articleId: string;
    qty: number;
    uom: string;
    price: number;
    taxKeyId?: string;
    deliveryDate?: Date;
  }) {
    this.id = data.id;
    this.poId = data.poId;
    this.articleId = data.articleId;
    this.qty = data.qty;
    this.uom = data.uom;
    this.price = data.price;
    this.taxKeyId = data.taxKeyId;
    this.deliveryDate = data.deliveryDate;
  }

  static create(data: {
    poId: string
    articleId: string
    qty: number
    uom: string
    price: number
    taxKeyId?: string
    deliveryDate?: Date
  }): PurchaseOrderItem {
    return new PurchaseOrderItem({
      id: '', // ID will be generated
      poId: data.poId,
      articleId: data.articleId,
      qty: data.qty,
      uom: data.uom,
      price: data.price,
      taxKeyId: data.taxKeyId,
      deliveryDate: data.deliveryDate
    })
  }

  get lineAmount(): number {
    return this.qty * this.price
  }

  withQuantity(newQty: number): PurchaseOrderItem {
    return new PurchaseOrderItem({
      id: this.id,
      poId: this.poId,
      articleId: this.articleId,
      qty: newQty,
      uom: this.uom,
      price: this.price,
      taxKeyId: this.taxKeyId,
      deliveryDate: this.deliveryDate
    })
  }

  withPrice(newPrice: number): PurchaseOrderItem {
    return new PurchaseOrderItem({
      id: this.id,
      poId: this.poId,
      articleId: this.articleId,
      qty: this.qty,
      uom: this.uom,
      price: newPrice,
      taxKeyId: this.taxKeyId,
      deliveryDate: this.deliveryDate
    })
  }
}